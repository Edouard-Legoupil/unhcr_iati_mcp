from __future__ import annotations

import logging
import uuid
from typing import Any

import httpx

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from unhcr_iati_mcp.config import settings


from unhcr_iati_mcp.observability.metrics import (
    monitor_datastore,
    complete_datastore,
    datastore_error,
)

from unhcr_iati_mcp.observability.logging import (
    get_logger,
)

logger = get_logger(__name__)

class IATIError(Exception):
    pass


class IATIAuthenticationError(IATIError):
    pass


class IATIRateLimitError(IATIError):
    pass


class IATIServerError(IATIError):
    pass


class IATIClient:

    def __init__(self):

        self.client = httpx.AsyncClient(
            timeout=settings.timeout_seconds,
            headers={
                "Ocp-Apim-Subscription-Key":
                    settings.iati_api_key,
                "Accept": "application/json",
            },
            limits=httpx.Limits(
                max_connections=50,
                max_keepalive_connections=20,
            ),
        )

    async def close(self):
        await self.client.aclose()

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(
            multiplier=1,
            min=2,
            max=30,
        ),
        retry=retry_if_exception_type(
            (
                httpx.TimeoutException,
                httpx.ConnectError,
                IATIServerError,
                IATIRateLimitError,
            )
        ),
        reraise=True,
    )
    async def query(
        self,
        collection: str,
        q: str,
        rows: int = 100,
        start: int = 0,
        fl: str = "*",
    ) -> dict[str, Any]:

        request_id = str(uuid.uuid4())

        url = (
            f"{settings.iati_base_url}/"
            f"{collection}/select"
        )

        logger.info(
            "[%s] Querying %s "
            "start=%s rows=%s",
            request_id,
            collection,
            start,
            rows,
        )

        try:

            response = await self.client.get(
                url,
                params={
                    "q": q,
                    "rows": rows,
                    "start": start,
                    "wt": "json",
                    "fl": fl,
                },
            )

        except httpx.TimeoutException as ex:

            logger.exception(
                "[%s] Timeout",
                request_id
            )

            raise

        except httpx.HTTPError as ex:

            logger.exception(
                "[%s] Network Error",
                request_id
            )

            raise

        if response.status_code == 401:

            raise IATIAuthenticationError(
                "Invalid API key"
            )

        if response.status_code == 403:

            raise IATIAuthenticationError(
                "Access denied"
            )

        if response.status_code == 429:

            raise IATIRateLimitError(
                "Rate limit exceeded"
            )

        if response.status_code >= 500:

            raise IATIServerError(
                response.text
            )

        response.raise_for_status()

        payload = response.json()

        if "response" not in payload:

            raise IATIError(
                "Malformed Datastore response"
            )

        num_found = (
            payload["response"]
            .get("numFound", 0)
        )

        logger.info(
            "[%s] Success "
            "records=%s",
            request_id,
            num_found,
        )

        return payload

    async def fetch_page(
        self,
        collection: str,
        q: str,
        page: int,
    ) -> dict[str, Any]:

        start = page * settings.page_size

        return await self.query(
            collection=collection,
            q=q,
            rows=settings.page_size,
            start=start,
        )

    async def fetch_all(
        self,
        collection: str,
        q: str,
        max_records: int | None = None,
    ) -> list[dict[str, Any]]:

        logger.info(
            "Starting bulk retrieval "
            "collection=%s",
            collection,
        )

        start = 0

        results = []

        page_size = settings.page_size

        while True:

            page = await self.query(
                collection=collection,
                q=q,
                rows=page_size,
                start=start,
            )

            docs = (
                page
                .get("response", {})
                .get("docs", [])
            )

            if not docs:

                logger.info(
                    "Pagination complete"
                )
                break

            results.extend(docs)

            logger.info(
                "Retrieved %s "
                "records so far",
                len(results),
            )

            if (
                max_records
                and len(results)
                >= max_records
            ):
                logger.info(
                    "Reached max_records "
                    "limit=%s",
                    max_records,
                )

                return results[:max_records]

            if len(docs) < page_size:
                break

            start += page_size

        logger.info(
            "Completed bulk retrieval "
            "total=%s",
            len(results),
        )

        return results

    async def fetch_all_with_metadata(
        self,
        collection: str,
        q: str,
    ):

        data = await self.fetch_all(
            collection=collection,
            q=q,
        )

        return {
            "collection": collection,
            "count": len(data),
            "data": data,
        }

    async def activities(
        self,
        q: str,
    ):
        return await self.fetch_all(
            "activity",
            q,
        )

    async def transactions(
        self,
        q: str,
    ):
        return await self.fetch_all(
            "transaction",
            q,
        )

    async def budgets(
        self,
        q: str,
    ):
        return await self.fetch_all(
            "budget",
            q,
        )