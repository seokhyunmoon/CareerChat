from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from string import Template

PROMPT_FILES_ROOT = Path(__file__).resolve().parent / "prompt_files"


@dataclass(frozen=True)
class RenderedPromptTemplate:
    system_prompt: str
    user_prompt: str


def render_prompt_template(
    template_path: str,
    variables: dict[str, str] | None = None,
) -> RenderedPromptTemplate:
    resolved_path = _resolve_template_path(template_path)
    template = Template(resolved_path.read_text(encoding="utf-8"))
    rendered = template.substitute(variables or {}).strip()

    return _split_rendered_prompt(rendered)


def _resolve_template_path(template_path: str) -> Path:
    resolved_path = (PROMPT_FILES_ROOT / template_path).resolve()
    if not resolved_path.is_relative_to(PROMPT_FILES_ROOT.resolve()):
        raise ValueError(f"Invalid prompt template path: {template_path}")
    if not resolved_path.is_file():
        raise FileNotFoundError(f"Prompt template not found: {template_path}")

    return resolved_path


def _split_rendered_prompt(rendered: str) -> RenderedPromptTemplate:
    system_marker = "# System"
    user_marker = "# User"
    system_start = rendered.find(system_marker)
    user_start = rendered.find(user_marker)

    if system_start == -1 or user_start == -1 or user_start <= system_start:
        raise ValueError("Prompt template must contain '# System' followed by '# User'")

    system_prompt = rendered[system_start + len(system_marker) : user_start].strip()
    user_prompt = rendered[user_start + len(user_marker) :].strip()
    if not system_prompt or not user_prompt:
        raise ValueError("Prompt template system and user sections must not be empty")

    return RenderedPromptTemplate(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )
