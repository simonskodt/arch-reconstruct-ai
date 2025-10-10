# Module: `src.retrieval`

> [!NOTE]
> This module is still missing the knowledge base and some testing.

## Quick Usage (From Project Root)

- Ensure API keys in `.env` are loaded.
- Run the builder as a package so relative imports work:

> [!IMPORTANT]
> We should set the dotenv in one of the first entry points of the program.

```bash
# From project root
uv run dotenv -f .env run -- python -m src.retrieval.builder
# Or, without uv/dotenv if env vars are already set:
python -m src.retrieval.builder
```
