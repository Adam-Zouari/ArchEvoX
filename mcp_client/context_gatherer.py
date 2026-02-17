"""MCP Client — Context Gatherer

Connects to the 3 MCP servers via stdio transport, calls their tools,
and assembles the enterprise context and patterns context strings that
are injected into agent prompts.
"""

import asyncio
import sys
from pathlib import Path
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def _call_tool(session: ClientSession, tool_name: str, arguments: dict | None = None) -> str:
    """Call a tool on an MCP server and return the text result."""
    arguments = arguments or {}
    result = await session.call_tool(tool_name, arguments)
    # result.content is a list of content blocks; join text blocks
    parts = []
    for block in result.content:
        if hasattr(block, "text"):
            parts.append(block.text)
    return "\n".join(parts)


async def _connect_and_call(
    server_module: str,
    data_dir: str,
    tool_calls: list[tuple[str, dict | None]],
) -> dict[str, str]:
    """Start an MCP server as a subprocess, connect, call tools, return results."""
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", server_module, str(data_dir)],
        cwd=str(Path(__file__).resolve().parent.parent),
    )

    async with AsyncExitStack() as stack:
        transport = await stack.enter_async_context(stdio_client(server_params))
        read_stream, write_stream = transport
        session = await stack.enter_async_context(ClientSession(read_stream, write_stream))
        await session.initialize()

        results = {}
        for tool_name, args in tool_calls:
            try:
                results[tool_name] = await _call_tool(session, tool_name, args)
            except Exception as e:
                results[tool_name] = f"[Error calling {tool_name}: {e}]"
        return results


async def gather_enterprise_context(config: dict | None = None) -> str:
    """Gather all enterprise context from the enterprise-docs and metadata MCP servers.

    Returns a single formatted string ready to inject into agent prompts.
    """
    if config is None:
        import yaml
        config_path = Path(__file__).resolve().parent.parent / "config.yaml"
        with open(config_path) as f:
            config = yaml.safe_load(f)

    mcp_cfg = config["mcp"]
    base_dir = Path(__file__).resolve().parent.parent

    enterprise_dir = str(base_dir / mcp_cfg["enterprise_docs"]["data_dir"])
    metadata_dir = str(base_dir / mcp_cfg["metadata"]["data_dir"])

    # Run both servers in parallel
    enterprise_task = _connect_and_call(
        "mcp_servers.enterprise_docs",
        enterprise_dir,
        [
            ("get_current_architecture", None),
            ("get_business_goals", None),
            ("get_constraints", None),
            ("get_team_profile", None),
            ("get_pain_points", None),
        ],
    )
    metadata_task = _connect_and_call(
        "mcp_servers.metadata",
        metadata_dir,
        [
            ("get_schema_inventory", None),
            ("get_pipeline_definitions", None),
            ("get_infrastructure_catalog", None),
            ("get_data_volume_stats", None),
        ],
    )

    enterprise_results, metadata_results = await asyncio.gather(
        enterprise_task, metadata_task
    )

    # Assemble into a structured context string
    sections = [
        ("Current Architecture", enterprise_results.get("get_current_architecture", "")),
        ("Business Goals", enterprise_results.get("get_business_goals", "")),
        ("Constraints", enterprise_results.get("get_constraints", "")),
        ("Team Profile", enterprise_results.get("get_team_profile", "")),
        ("Pain Points", enterprise_results.get("get_pain_points", "")),
        ("Schema Inventory", metadata_results.get("get_schema_inventory", "")),
        ("Pipeline Definitions", metadata_results.get("get_pipeline_definitions", "")),
        ("Infrastructure Catalog", metadata_results.get("get_infrastructure_catalog", "")),
        ("Data Volume Statistics", metadata_results.get("get_data_volume_stats", "")),
    ]

    parts = []
    for title, content in sections:
        parts.append(f"### {title}\n\n{content}")

    return "\n\n---\n\n".join(parts)


async def gather_patterns_context(config: dict | None = None) -> str:
    """Gather architectural patterns context from the patterns-knowledge MCP server.

    Returns a single formatted string with cross-domain analogies and emerging patterns.
    """
    if config is None:
        import yaml
        config_path = Path(__file__).resolve().parent.parent / "config.yaml"
        with open(config_path) as f:
            config = yaml.safe_load(f)

    mcp_cfg = config["mcp"]
    base_dir = Path(__file__).resolve().parent.parent
    patterns_dir = str(base_dir / mcp_cfg["patterns_knowledge"]["data_dir"])

    results = await _connect_and_call(
        "mcp_servers.patterns_knowledge",
        patterns_dir,
        [
            ("get_emerging_patterns", None),
            ("get_cross_domain_analogies", {"source_domain": "biological", "target_concept": "data routing"}),
            ("get_cross_domain_analogies", {"source_domain": "economic", "target_concept": "resource allocation"}),
            ("get_cross_domain_analogies", {"source_domain": "physical", "target_concept": "flow control"}),
        ],
    )

    sections = [
        ("Emerging Patterns", results.get("get_emerging_patterns", "")),
        ("Cross-Domain Analogies", "\n\n".join(
            v for k, v in results.items() if k == "get_cross_domain_analogies"
        ) if any(k == "get_cross_domain_analogies" for k in results) else ""),
    ]

    # Since dict keys are unique and we called get_cross_domain_analogies multiple times,
    # we need a different approach — use a list to preserve all results
    parts = [f"### Emerging Patterns\n\n{results.get('get_emerging_patterns', '')}"]

    # Collect all cross-domain results
    for key, value in results.items():
        if key != "get_emerging_patterns":
            parts.append(f"### Cross-Domain Analogy\n\n{value}")

    return "\n\n---\n\n".join(parts)


async def gather_paradigm_patterns(config: dict | None = None) -> dict[str, str]:
    """Fetch paradigm-specific patterns from the patterns-knowledge MCP server.

    Returns dict mapping paradigm name to patterns text, used by Stage 0b
    (Prompt Enhancement) to enrich each agent's system prompt with relevant patterns.
    """
    if config is None:
        import yaml
        config_path = Path(__file__).resolve().parent.parent / "config.yaml"
        with open(config_path) as f:
            config = yaml.safe_load(f)

    mcp_cfg = config["mcp"]
    base_dir = Path(__file__).resolve().parent.parent
    patterns_dir = str(base_dir / mcp_cfg["patterns_knowledge"]["data_dir"])

    paradigm_queries = {
        "streaming": [("get_patterns_by_paradigm", {"paradigm": "streaming"})],
        "event_sourcing": [("get_patterns_by_paradigm", {"paradigm": "event-sourcing"})],
        "declarative": [("get_patterns_by_paradigm", {"paradigm": "declarative"})],
        "wildcard": [
            ("get_cross_domain_analogies", {"source_domain": "biological", "target_concept": "data pipeline"}),
            ("get_cross_domain_analogies", {"source_domain": "economic", "target_concept": "resource allocation"}),
            ("get_emerging_patterns", None),
        ],
    }

    results: dict[str, str] = {}

    for agent_name, tool_calls in paradigm_queries.items():
        try:
            server_results = await _connect_and_call(
                "mcp_servers.patterns_knowledge",
                patterns_dir,
                tool_calls,
            )
            # Combine all results for this paradigm
            parts = [v for v in server_results.values() if v and not v.startswith("[Error")]
            results[agent_name] = "\n\n---\n\n".join(parts) if parts else ""
        except Exception as e:
            results[agent_name] = f"[Error gathering patterns for {agent_name}: {e}]"

    return results
