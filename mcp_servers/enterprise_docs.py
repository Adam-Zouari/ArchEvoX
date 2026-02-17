"""MCP Server: enterprise-docs-server

Serves enterprise documentation — current architecture descriptions,
business goals, constraints, SLAs, team structure, compliance requirements.
"""

import sys
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server

server = Server("enterprise-docs-server")

# Data directory is passed as a command-line argument
_data_dir: Path | None = None


def _load_file(name: str) -> str:
    """Load a file from the data directory, returning its contents or a fallback message."""
    if _data_dir is None:
        return "No data directory configured."
    # Try exact match first, then glob for partial match
    for path in _data_dir.iterdir():
        if path.is_file() and name.lower() in path.stem.lower():
            return path.read_text(encoding="utf-8")
    return f"No file matching '{name}' found in {_data_dir}"


def _load_all() -> str:
    """Load all files from the data directory."""
    if _data_dir is None:
        return "No data directory configured."
    parts = []
    for path in sorted(_data_dir.iterdir()):
        if path.is_file():
            parts.append(f"## {path.name}\n\n{path.read_text(encoding='utf-8')}")
    return "\n\n---\n\n".join(parts) if parts else "No files found in data directory."


@server.tool()
async def get_current_architecture() -> str:
    """Returns the full description of the current data pipeline architecture,
    including component inventory, data flow diagrams (as text), and technology stack."""
    return _load_file("architecture")


@server.tool()
async def get_business_goals() -> str:
    """Returns the business goals, KPIs, and strategic priorities that the
    data pipeline must support."""
    return _load_file("business_goals")


@server.tool()
async def get_constraints() -> str:
    """Returns hard constraints: regulatory/compliance requirements, budget limits,
    SLAs, latency requirements, data residency rules, security mandates."""
    return _load_file("constraints")


@server.tool()
async def get_team_profile() -> str:
    """Returns team skills, size, experience level, and organizational structure
    relevant to architecture decisions."""
    return _load_file("team")


@server.tool()
async def get_pain_points() -> str:
    """Returns known pain points, bottlenecks, incidents, and technical debt
    in the current architecture."""
    return _load_file("pain_points")


async def main():
    global _data_dir
    if len(sys.argv) > 1:
        _data_dir = Path(sys.argv[1])
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
