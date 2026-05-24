# CareerChat AI

This folder contains the AI backend foundation and the prototype analysis pipeline.

The prototype code is kept under `app/prototype` as reference material. Production
AI backend work should use the foundation packages under `app/api`, `app/workers`,
`app/pipeline`, `app/prompts`, `app/retrieval`, `app/llm`, `app/callbacks`,
`app/core`, and `app/schemas`.

## Setup

```bash
cd apps/ai
uv sync
cp -n .env.example .env
```

Then edit `.env` and set:

```env
GROQ_API_KEY=your_real_groq_api_key
```

## Run Sample

Analyze the bundled sample data:

```bash
uv run python -m app.prototype.samples.run_sample
```

Run only one sample job posting to reduce LLM calls:

```bash
uv run python -m app.prototype.samples.run_sample --max-jobs 1
```

## Pipeline

```plain text
build_profile_documents
  -> selective_split_profile_docs
  -> create_retriever
  -> structure_job_posting
  -> match_requirements
  -> compute_fit_score
  -> generate_report
```
