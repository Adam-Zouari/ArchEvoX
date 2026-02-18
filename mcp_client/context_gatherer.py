"""Context Gatherer — Simplified Version (Direct File Reading)

Instead of MCP servers, directly read files from input directories.
This is simpler and works the same for local files.
"""

from pathlib import Path


async def gather_enterprise_context(config=None):
    """Read all enterprise docs and metadata from local files."""
    base_dir = Path(__file__).parent.parent

    sections = []

    # Read enterprise docs
    docs_dir = base_dir / "input/enterprise_docs"
    if docs_dir.exists():
        for file in sorted(docs_dir.glob("*.md")):
            if file.name != "README.md":
                try:
                    content = file.read_text(encoding="utf-8")
                    sections.append(f"### {file.stem.replace('_', ' ').title()}\n\n{content}")
                except Exception as e:
                    sections.append(f"### {file.stem}\n\n[Error reading file: {e}]")

    # Read metadata
    metadata_dir = base_dir / "input/metadata"
    if metadata_dir.exists():
        for file in sorted(metadata_dir.glob("*")):
            if file.suffix in [".json", ".yaml", ".yml", ".txt"] and file.name != "README.md":
                try:
                    content = file.read_text(encoding="utf-8")
                    sections.append(f"### {file.stem.replace('_', ' ').title()}\n\n{content}")
                except Exception as e:
                    sections.append(f"### {file.stem}\n\n[Error reading file: {e}]")

    if not sections:
        return "[No enterprise documentation found in input/ directories]"

    return "\n\n---\n\n".join(sections)


async def gather_patterns_context(config=None):
    """Read patterns from knowledge base."""
    base_dir = Path(__file__).parent.parent
    kb_dir = base_dir / "knowledge_base"

    sections = []
    if kb_dir.exists():
        # Read specific pattern files for general context
        for pattern_type in ["emerging_patterns", "streaming_patterns", "event_sourcing_patterns"]:
            for file in kb_dir.glob(f"{pattern_type}.md"):
                try:
                    content = file.read_text(encoding="utf-8")
                    sections.append(f"### {file.stem.replace('_', ' ').title()}\n\n{content}")
                except Exception as e:
                    sections.append(f"### {file.stem}\n\n[Error reading file: {e}]")

    if not sections:
        return "[No pattern knowledge base found]"

    return "\n\n---\n\n".join(sections)


async def gather_paradigm_patterns(config=None):
    """Fetch paradigm-specific patterns from the knowledge base.

    Returns dict mapping paradigm name to patterns text, used by Stage 0b
    (Prompt Enhancement) to enrich each agent's system prompt.
    """
    base_dir = Path(__file__).parent.parent
    kb_dir = base_dir / "knowledge_base"

    paradigm_files = {
        "streaming": ["streaming_patterns.md"],
        "event_sourcing": ["event_sourcing_patterns.md"],
        "declarative": ["declarative_patterns.md"],
        "wildcard": ["biological_analogies.md", "economic_analogies.md",
                     "physical_analogies.md", "emerging_patterns.md"],
    }

    results = {}

    for agent_name, filenames in paradigm_files.items():
        parts = []
        for filename in filenames:
            file_path = kb_dir / filename
            if file_path.exists():
                try:
                    content = file_path.read_text(encoding="utf-8")
                    parts.append(content)
                except Exception as e:
                    parts.append(f"[Error reading {filename}: {e}]")

        results[agent_name] = "\n\n---\n\n".join(parts) if parts else ""

    return results
