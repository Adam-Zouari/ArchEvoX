"""MCP Server: metadata-server

Serves technical metadata — schemas, data catalogs, pipeline definitions,
infrastructure inventory.
"""

import sys
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server

server = Server("metadata-server")

_data_dir: Path | None = None


def _load_file(name: str) -> str:
    """Load a file from the data directory matching the given name."""
    if _data_dir is None:
        return "No data directory configured."
    for path in _data_dir.iterdir():
        if path.is_file() and name.lower() in path.stem.lower():
            return path.read_text(encoding="utf-8")
    return f"No file matching '{name}' found in {_data_dir}"


def _search_files(query: str) -> str:
    """Search across all files for content matching the query."""
    if _data_dir is None:
        return "No data directory configured."
    results = []
    query_lower = query.lower()
    for path in sorted(_data_dir.iterdir()):
        if path.is_file():
            content = path.read_text(encoding="utf-8")
            if query_lower in content.lower():
                results.append(f"## {path.name}\n\n{content}")
    return "\n\n---\n\n".join(results) if results else f"No results for '{query}'"


@server.tool()
async def get_schema_inventory() -> str:
    """Returns all known data schemas — tables, columns, types, relationships,
    lineage information. Formatted as structured text or JSON."""
    return _load_file("schema")


@server.tool()
async def get_pipeline_definitions() -> str:
    """Returns current pipeline/job definitions — DAGs, schedules, dependencies,
    transformation logic summaries."""
    return _load_file("pipeline")


@server.tool()
async def get_infrastructure_catalog() -> str:
    """Returns deployed infrastructure — databases, message queues, compute
    clusters, storage systems, orchestrators, with versions and configurations."""
    return _load_file("infrastructure")


@server.tool()
async def get_data_volume_stats() -> str:
    """Returns data volume statistics — ingestion rates, storage sizes,
    query patterns, peak load profiles."""
    return _load_file("volume")


@server.tool()
async def search_metadata(query: str) -> str:
    """Free-text search across all metadata. Use when looking for specific
    tables, pipelines, technologies, or configurations."""
    return _search_files(query)


async def main():
    global _data_dir
    if len(sys.argv) > 1:
        _data_dir = Path(sys.argv[1])
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
