"""
IATI Datastore Client for UNHCR MCP Server.

This module provides an async HTTP client for querying the IATI Datastore API
with automatic retry logic, error handling, and metrics integration.
"""

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
    datastore_latency,
)

from unhcr_iati_mcp.observability.logging import (
    get_logger,
)

logger = get_logger(__name__)


class IATIError(Exception):
    """Base exception for IATI Datastore errors."""
    pass


class IATIAuthenticationError(IATIError):
    """Exception raised for authentication errors (401, 403)."""
    pass


class IATIRateLimitError(IATIError):
    """Exception raised when rate limit is exceeded (429)."""
    pass


class IATIServerError(IATIError):
    """Exception raised for server errors (5xx)."""
    pass


class IATIClient:
    """
    Async HTTP client for the IATI Datastore API.
    
    Features:
    - Connection pooling with configurable limits
    - Automatic retry with exponential backoff
    - Prometheus metrics integration
    - Structured logging
    - Custom error hierarchy
    
    Attributes:
        client: HTTPX async client instance
    """

    def __init__(self):
        """Initialize the IATI client with connection pooling and headers."""
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
        """Close the HTTP client and release connections."""
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
        """
        Query the IATI Datastore API.
        
        Args:
            collection: The collection to query (activity, transaction, budget)
            q: Solr query string
            rows: Number of results to return
            start: Starting offset for pagination
            fl: Fields to return (default: all)
            
        Returns:
            Dictionary containing the API response with 'response' key
            
        Raises:
            IATIAuthenticationError: If authentication fails (401, 403)
            IATIRateLimitError: If rate limit is exceeded (429)
            IATIServerError: If server error occurs (5xx)
            IATIError: If response is malformed
            httpx.TimeoutException: If request times out
            httpx.HTTPError: If HTTP error occurs
        """
        import time
        
        request_id = str(uuid.uuid4())
        start_time = time.time()

        # Track metrics
        monitor_datastore(collection)

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
            datastore_error(collection, "timeout")
            raise

        except httpx.HTTPError as ex:

            logger.exception(
                "[%s] Network Error",
                request_id
            )
            datastore_error(collection, "network_error")
            raise

        # Track latency
        latency = time.time() - start_time
        datastore_latency.labels(collection=collection).observe(latency)

        if response.status_code == 401:
            datastore_error(collection, "authentication_error")
            complete_datastore(collection, "authentication_error")
            raise IATIAuthenticationError(
                "Invalid API key"
            )

        if response.status_code == 403:
            datastore_error(collection, "authentication_error")
            complete_datastore(collection, "authentication_error")
            raise IATIAuthenticationError(
                "Access denied"
            )

        if response.status_code == 429:
            datastore_error(collection, "rate_limit_error")
            complete_datastore(collection, "rate_limit_error")
            raise IATIRateLimitError(
                "Rate limit exceeded"
            )

        if response.status_code >= 500:
            datastore_error(collection, "server_error")
            complete_datastore(collection, "server_error")
            raise IATIServerError(
                response.text
            )

        response.raise_for_status()
        
        complete_datastore(collection, "success")

        payload = response.json()

        if "response" not in payload:
            datastore_error(collection, "malformed_response")
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
        """
        Fetch a single page of results.
        
        Args:
            collection: The collection to query
            q: Solr query string
            page: Page number (0-indexed)
            
        Returns:
            Dictionary containing the API response
        """
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
        """
        Fetch all results with automatic pagination.
        
        Args:
            collection: The collection to query
            q: Solr query string
            max_records: Maximum number of records to return (optional)
            
        Returns:
            List of all matching documents
        """
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
    ) -> dict[str, Any]:
        """
        Fetch all results with metadata.
        
        Args:
            collection: The collection to query
            q: Solr query string
            
        Returns:
            Dictionary containing collection name, count, and data
        """
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
    ) -> list[dict[str, Any]]:
        """
        Fetch all activities matching the query.
        
        Args:
            q: Solr query string
            
        Returns:
            List of activity documents
        """
        return await self.fetch_all(
            "activity",
            q,
        )

    async def transactions(
        self,
        q: str,
    ) -> list[dict[str, Any]]:
        """
        Fetch all transactions matching the query.
        
        Args:
            q: Solr query string
            
        Returns:
            List of transaction documents
        """
        return await self.fetch_all(
            "transaction",
            q,
        )

    async def budgets(
        self,
        q: str,
    ) -> list[dict[str, Any]]:
        """
        Fetch all budgets matching the query.
        
        Args:
            q: Solr query string
            
        Returns:
            List of budget documents
        """
        return await self.fetch_all(
            "budget",
            q,
        )
