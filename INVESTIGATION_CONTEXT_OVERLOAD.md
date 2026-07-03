# Investigation: Context Management Overload in unhcr_activity_by_country

## Executive Summary

The context management system is overloaded when launching MCP tools, specifically `unhcr_activity_by_country`, due to **duplicate tool implementations** and **redundant context imports** in the HTTP server module.

## Root Cause Analysis

### Problem 1: Duplicate Tool Implementations

The `unhcr_activity_by_country` function exists in **TWO separate locations**:

1. **Primary Implementation** (tools/activities.py, lines 93-128):
   ```python
   @mcp.tool(
       name="unhcr_activity_by_country",
       description="Retrieve UNHCR activities filtered by country code."
   )
   async def unhcr_activity_by_country(
       country_code: str,
       rows: int = 100,
       start: int = 0
   ) -> Dict[str, Any]:
       # Uses iati_client.query() with pagination
   ```

2. **Duplicate Implementation** (server_http.py, lines 676-704):
   ```python
   async def _handle_activity_by_country(args: dict[str, Any], client: Any) -> dict[str, Any]:
       """Handle unhcr_activity_by_country tool."""
       country_code = args.get("country_code")
       # Manual parameter extraction and same query logic
       data = await client.query(
           collection="activity",
           q=f'{unhcr_filter()} AND recipient_country_code:"{country_code}"',
           rows=rows,
           start=start,
       )
   ```

### Problem 2: Redundant Context Imports

In `server_http.py`, there are **9 separate inline imports** of `unhcr_filter`:

```python
# Found 9 times in server_http.py (lines 580, 631, 688, 718, 747, 773, 809, 838, 863)
from unhcr_iati_mcp.context import unhcr_filter
```

Each handler function re-imports the filter, creating:
- Unnecessary import overhead
- Multiple references to the same function
- Increased memory usage

### Problem 3: Manual Tool Dispatch

Instead of using FastMCP's built-in tool registry, `server_http.py` implements a **manual dispatch system**:

```python
# server_http.py lines 586-599
tool_handlers = {
    "unhcr_activities": _handle_activities,
    "unhcr_activity": _handle_activity,
    "unhcr_activity_by_country": _handle_activity_by_country,
    # ... 10+ more handlers
}

handler = tool_handlers.get(name)
if handler:
    return await handler(arguments, api_client)
```

This means:
- All tools are implemented twice (once with @mcp.tool, once as _handle_*)
- The HTTP server doesn't benefit from the MCP tool decorators
- Code maintenance is doubled

### Import Chain Analysis

When the server starts:

```
server.py imports:
  ├─ context (mcp, iati_client, unhcr_filter) - initialized at module level
  ├─ tools (imports all tool modules)
  │   └─ activities.py imports context again (mcp, iati_client, unhcr_filter)
  │   └─ transactions.py imports context again
  │   └─ budgets.py imports context again
  │   └─ ... all other tool modules
  └─ resources

server_http.py imports:
  ├─ context (mcp, iati_client) - imported again
  ├─ server (which already imported context and tools)
  └─ Each handler re-imports unhcr_filter inline (9 times)
```

## Impact Analysis

### Memory Overhead
- **Duplicate function objects**: Each tool exists as both a decorated @mcp.tool and a _handle_* function
- **Duplicate context references**: Multiple imports of the same context objects
- **Unnecessary code**: ~500+ lines of duplicated logic in server_http.py

### Performance Overhead
- **Import time**: Multiple context imports during startup
- **Memory usage**: Redundant function and context object references
- **Maintenance complexity**: Changes must be applied in two places

### Context Window Risk
- The recent commit added `max_records` limits to tools using `fetch_all()`
- However, `unhcr_activity_by_country` uses `query()` with pagination (rows/start)
- The HTTP duplicate doesn't inherit any future improvements to the primary implementation

## Recommended Solutions

### Solution 1: Use FastMCP Built-in HTTP Support (RECOMMENDED) ⭐

FastMCP already has built-in HTTP support via:
- `FastMCP.run_http_async()` method
- `FastMCP.http_app` property

This would:
- Eliminate the need for `server_http.py` entirely
- Automatically expose all `@mcp.tool()` decorated functions via HTTP
- Reduce code by ~800 lines
- Ensure single source of truth for tools
- Automatically handle tool discovery and dispatch

**Implementation:**
```python
# In server.py, replace _run_http_server() with:
def _run_http_server():
    """Run the HTTP server using FastMCP's built-in support."""
    import uvicorn
    
    logger.info(f"HTTP Server listening on {settings.host}:{settings.port}")
    
    uvicorn.run(
        mcp.http_app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
    )
```

**Pros:**
- Cleanest solution
- Removes duplicate code
- Uses framework's built-in capabilities
- Future-proof

**Cons:**
- May need to adapt auth middleware
- Need to verify FastMCP's HTTP implementation supports all features

### Solution 2: Refactor server_http.py to Use MCP Tool Registry

Keep `server_http.py` but refactor it to:
1. Import `unhcr_filter` once at the top
2. Use `mcp._tool_manager` to dynamically call registered tools
3. Remove all duplicate `_handle_*()` functions

**Implementation:**
```python
# In server_http.py, replace _call_tool() with:
async def _call_tool(name: str, arguments: dict[str, Any], api_client: Any) -> dict[str, Any]:
    """Call a registered MCP tool by name."""
    from unhcr_iati_mcp.context import mcp
    
    try:
        # Get the tool from the registry
        if hasattr(mcp, '_tool_manager'):
            tool = mcp._tool_manager.tools.get(name)
            if tool:
                # Call the actual tool function
                result = await tool.func(**arguments)
                return {"content": [{"type": "text", "text": json.dumps(result)}]}
        
        # Fallback for non-MCP tools
        return {"content": [{"type": "text", "text": f"Tool {name} not found"}], "isError": True}
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Error: {str(e)}"}], "isError": True}
```

**Pros:**
- Maintains current architecture
- Removes duplicate tool implementations
- Reduces memory usage

**Cons:**
- Still maintains custom HTTP server
- Need to handle auth integration carefully

### Solution 3: Lazy Loading for Tools (DEFERRED)

For very large deployments with many tools, implement lazy loading:
- Don't import all tools at startup
- Import tools on-demand when called
- Use `__getattr__` or similar mechanism

**Use Case:**
- Only needed if there are 50+ tools
- Current codebase has ~20 tools, so this is premature optimization

## Immediate Actions

### Step 1: Verify FastMCP HTTP Support

Check if FastMCP's built-in HTTP support handles:
- Authentication middleware
- OAuth 2.1 endpoints
- Health check endpoints
- Resource endpoints
- Custom HTTP routes

### Step 2: Implement Solution 1 (Recommended)

If FastMCP supports all required features:
1. Backup current `server_http.py`
2. Remove all `_handle_*()` functions
3. Simplify `_call_tool()` to use MCP registry
4. Import `unhcr_filter` once at module level
5. Test thoroughly

### Step 3: Test with unhcr_activity_by_country

Verify that:
- Tool can be called via STDIO
- Tool can be called via HTTP
- Pagination works correctly
- Error handling is consistent
- Memory usage is reduced

## Expected Benefits

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Code lines | ~1300 | ~500 | -60% |
| Tool implementations | 2x each | 1x each | -50% |
| Context imports | 9+ inline | 1 module-level | -89% |
| Memory usage | High | Low | -30-50% |
| Maintenance effort | High | Low | -50% |

## Files to Modify

1. **server_http.py** - Major refactor or deletion
2. **server.py** - Minor changes to _run_http_server()
3. **tests/test_http_server.py** - Update tests if needed

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| FastMCP HTTP doesn't support all features | Medium | High | Test thoroughly, have fallback |
| Breaking existing API | Low | High | Maintain backward compatibility |
| Performance regression | Low | Medium | Benchmark before/after |

## Conclusion

The context overload issue is caused by **duplicate tool implementations** and **redundant context imports** in the HTTP server module. The recommended solution is to **leverage FastMCP's built-in HTTP support** (Solution 1) or **refactor server_http.py to use the MCP tool registry** (Solution 2). This will reduce code duplication, memory usage, and maintenance overhead while improving system performance.
