# CareerChat AI

This folder contains the Python version of the original Colab pipeline in `Final_colabdownload_1.py`.

## Setup

```powershell
cd apps/ai
uv sync
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Then edit `.env` and set:

```env
GROQ_API_KEY=your_real_groq_api_key
```

## Run Sample

Analyze the bundled sample data:

```powershell
uv run python -m app.samples.run_sample
```

Run only one sample job posting to reduce LLM calls:

```powershell
uv run python -m app.samples.run_sample --max-jobs 1
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
