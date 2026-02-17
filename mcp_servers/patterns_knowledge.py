"""MCP Server: patterns-knowledge-server

Provides a knowledge base of architectural patterns — both conventional and
unconventional — that agents can query for inspiration.
"""

import sys
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server

server = Server("patterns-knowledge-server")

_data_dir: Path | None = None


def _load_file(name: str) -> str:
    """Load a file from the knowledge base matching the given name."""
    if _data_dir is None:
        return "No data directory configured."
    for path in _data_dir.iterdir():
        if path.is_file() and name.lower() in path.stem.lower():
            return path.read_text(encoding="utf-8")
    return f"No file matching '{name}' found in {_data_dir}"


def _load_multiple(names: list[str]) -> str:
    """Load and concatenate files matching any of the given names."""
    if _data_dir is None:
        return "No data directory configured."
    parts = []
    for path in sorted(_data_dir.iterdir()):
        if path.is_file():
            stem_lower = path.stem.lower()
            if any(n.lower() in stem_lower for n in names):
                parts.append(f"## {path.name}\n\n{path.read_text(encoding='utf-8')}")
    return "\n\n---\n\n".join(parts) if parts else "No matching files found."


@server.tool()
async def get_patterns_by_paradigm(paradigm: str) -> str:
    """Returns architectural patterns for a given paradigm.
    Supported paradigms: 'streaming', 'event-sourcing', 'declarative',
    'graph-native', 'lakehouse', 'data-mesh', 'data-fabric',
    'biological', 'economic', 'physical', 'social'.
    Returns: pattern name, description, key components, known tradeoffs,
    real-world examples."""
    return _load_file(paradigm)


@server.tool()
async def get_cross_domain_analogies(source_domain: str, target_concept: str) -> str:
    """Given a source domain (e.g., 'immunology', 'supply-chain', 'thermodynamics')
    and a target concept (e.g., 'data routing', 'error handling', 'resource allocation'),
    returns known cross-domain pattern mappings with concrete architectural translations."""
    return _load_multiple([source_domain, target_concept, "analogies"])


@server.tool()
async def get_emerging_patterns() -> str:
    """Returns recently emerging or experimental architectural patterns that
    are not yet mainstream. Includes academic proposals, startup architectures,
    and unconventional production systems."""
    return _load_file("emerging")


@server.tool()
async def get_anti_patterns() -> str:
    """Returns common architectural anti-patterns and their failure modes.
    Useful for the physics critic and self-refinement stages to check
    proposals against known bad patterns."""
    return _load_file("anti_pattern")


async def main():
    global _data_dir
    if len(sys.argv) > 1:
        _data_dir = Path(sys.argv[1])
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
