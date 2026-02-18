# Quick Start Guide

## Step 1: Install Dependencies

```bash
cd innovation_arch_generator
pip install -r requirements.txt
```

## Step 2: Choose Your LLM Provider

### Option A: Ollama (Local, Free, Recommended for Testing)

1. Install Ollama from https://ollama.com/
2. Pull a model:
   ```bash
   ollama pull qwen2.5:3b
   # or: ollama pull llama3.2
   # or: ollama pull deepseek-r1:8b
   ```
3. The `config.yaml` is already set for Ollama by default
4. **No API key needed!**

### Option B: Anthropic Claude (Cloud, Paid)

1. Get your API key from https://console.anthropic.com/
2. Set the environment variable:
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-..."
   ```
3. Edit `config.yaml`:
   ```yaml
   llm:
     model: "anthropic/claude-sonnet-4-20250514"
     api_base: null  # Remove the Ollama URL
   ```

### Option C: OpenAI (Cloud, Paid)

1. Get your API key from https://platform.openai.com/
2. Set the environment variable:
   ```bash
   export OPENAI_API_KEY="sk-..."
   ```
3. Edit `config.yaml`:
   ```yaml
   llm:
     model: "openai/gpt-4o"
     api_base: null
   ```

## Step 3: Provide Your Documentation (CRITICAL)

⚠️ **The example files are for a fictional company. You MUST replace them with your own.**

Navigate to `input/` and replace the example files:

**Minimum required:**
- `input/enterprise_docs/architecture.md` — Your current data pipeline architecture
- `input/enterprise_docs/pain_points.md` — What problems you're trying to solve

**Recommended to add:**
- `input/enterprise_docs/business_goals.md` — Your business objectives
- `input/enterprise_docs/constraints.md` — Budget, compliance, SLAs
- `input/enterprise_docs/team.md` — Team size and skills
- `input/metadata/schema_inventory.json` — Your database schemas
- `input/metadata/infrastructure_catalog.json` — Your deployed infrastructure

See `input/README.md`, `input/enterprise_docs/README.md`, and `input/metadata/README.md` for detailed templates.

## Step 4: Run the System

```bash
python main.py
```

**Expected runtime**: 15-45 minutes depending on:
- Your model (local models are slower but free)
- Which stages are enabled in `config.yaml`
- Number of proposals generated

**What happens:**
1. MCP servers start and load your documentation
2. **Stage 0a**: Intent agent analyzes your context
3. **Stage 0b**: Prompts are enhanced with intent insights
4. **Stage 1**: 4 paradigm agents generate proposals in parallel
5. **Stage 2**: Mutation operators create variants
6. **Stage 2.5**: Diversity archive selects the best diverse subset
7. **Stage 3**: Self-refinement strengthens proposals
8. **Stage 4**: Physics critic annotates constraints
9. **Stage 4.5**: Structured debates evaluate proposals
10. **Stage 4.7**: Domain critics (security, cost, org, data quality) review
11. **Stage 5**: Portfolio ranking and assembly

## Step 5: Review Output

Check the `outputs/` directory:

**`outputs/portfolio.json`** — Full structured data with all proposals, scores, and annotations

**`outputs/portfolio_report.md`** — Human-readable report with:
- Executive summary
- Top picks by tier (conservative, moderate, radical)
- Full details of each proposal with scores, components, risks, and annotations

## Troubleshooting

### "ModuleNotFoundError: No module named 'instructor'"

```bash
pip install -r requirements.txt
```

### "Connection refused" (Ollama)

Make sure Ollama is running:
```bash
ollama serve
```

### "No proposals generated in Stage 1"

- Check your API key is set correctly
- Check you have credits/quota with your LLM provider
- Try a different model
- Check the logs for specific error messages

### "Only X proposals survived to Stage 5"

This is normal — some LLM calls may fail. As long as ≥6 proposals reach the end, you'll get a useful portfolio.

### Takes too long / too expensive

Disable some stages in `config.yaml`:

```yaml
pipeline:
  intent_agent:
    enabled: false
  diversity_archive:
    enabled: false
  structured_debate:
    enabled: false
  domain_critics:
    enabled: false
```

Or use a faster/cheaper model like `ollama_chat/qwen2.5:3b`.

## Testing with Example Data

If you want to test the system FIRST before providing your own data:

1. The example files are already in place (fictional e-commerce company)
2. Just run `python main.py`
3. Review the output to understand the format
4. Then replace with your real data and run again

## Next Steps

- Read `README.md` for full documentation
- Adjust `config.yaml` to tune temperatures, weights, enabled stages
- Extend `knowledge_base/` with additional architectural patterns
- Review the proposals and select one to refine with your team

---

**Need help?** See the full `README.md` or check `input/README.md` for documentation templates.
