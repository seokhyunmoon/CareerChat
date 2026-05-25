from __future__ import annotations

from pathlib import Path
from string import Template

PROMPT_FILES_ROOT = Path(__file__).resolve().parent / "prompt_files"


def render_prompt_template(
    template_path: str,
    variables: dict[str, str] | None = None,
) -> str:
    resolved_path = _resolve_template_path(template_path)
    template = Template(resolved_path.read_text(encoding="utf-8"))

    return template.substitute(variables or {}).strip()


def _resolve_template_path(template_path: str) -> Path:
    resolved_path = (PROMPT_FILES_ROOT / template_path).resolve()
    if not resolved_path.is_relative_to(PROMPT_FILES_ROOT.resolve()):
        raise ValueError(f"Invalid prompt template path: {template_path}")
    if not resolved_path.is_file():
        raise FileNotFoundError(f"Prompt template not found: {template_path}")

    return resolved_path
