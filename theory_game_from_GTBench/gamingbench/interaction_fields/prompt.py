from __future__ import annotations

import json
from typing import Any

from gamingbench.interaction_fields.schemas import CompiledDecisionProgram, is_unavailable


DEFAULT_FINAL_OUTPUT_SCHEMA = {
    "action": "...",
    "used_rule": "P?",
    "used_fields": ["..."],
    "verifier_passed": True,
}


MATRIX_FINAL_OUTPUT_SCHEMA = {
    "answer": [["A1", "B2"]],
    "used_fields": ["mutual_best_response_cells"],
    "verifier_passed": True,
}


def _format_value(value: Any, indent: str = "  ") -> str:
    if isinstance(value, dict):
        lines = []
        for key, item in value.items():
            if isinstance(item, (dict, list)):
                rendered = json.dumps(item, ensure_ascii=False)
            else:
                rendered = item
            lines.append(f"{indent}{key}: {rendered}")
        return "\n".join(lines) if lines else f"{indent}{{}}"
    if isinstance(value, list):
        return f"{indent}{json.dumps(value, ensure_ascii=False)}"
    return f"{indent}{json.dumps(value, ensure_ascii=False)}"


def _calculation_text(field) -> str:
    if field.calculation.get("formula"):
        return field.calculation["formula"]
    steps = field.calculation.get("steps") or []
    if not steps:
        return field.calculation.get("method", "")
    if len(steps) == 1:
        return steps[0]
    return " ".join(steps[:2])


def _render_field(field) -> str:
    lines = [
        f"- {field.field_id}:",
        f"  Role: {field.decision_role}",
        f"  Operator: {field.operator}",
    ]
    if field.priority is not None:
        lines.append(f"  Priority: {field.priority}")
    lines.append(f"  Calculation: {_calculation_text(field)}")
    if is_unavailable(field.value):
        lines.append("  Value: unavailable")
        lines.append(f"  Reason: {field.value.get('reason', '')}")
    else:
        lines.append("  Value:")
        lines.append(_format_value(field.value, indent="    "))
    return "\n".join(lines)


def _render_rule(index: int, rule) -> str:
    if rule.operator == "filter":
        action = f"Exclude actions listed in {rule.field_id}."
    elif rule.operator == "choose_if_nonempty":
        action = f"If {rule.field_id} is non-empty and available, choose from it."
    elif rule.operator == "maximize":
        action = f"If {rule.field_id} is available, choose the remaining legal action with the highest value."
    elif rule.operator == "minimize":
        action = f"If {rule.field_id} is available, choose the remaining legal action with the lowest value."
    elif rule.operator == "intersection":
        action = f"Return the complete set in {rule.field_id}."
    else:
        action = rule.description
    return f"P{index}. {action} ({rule.rule_id})"


def _render_verifier(check) -> str:
    if check.field_id:
        return f"- {check.check_id}: {check.condition} [field: {check.field_id}]"
    return f"- {check.check_id}: {check.condition}"


def build_small_model_prompt(program: CompiledDecisionProgram, state_summary: str = "") -> str:
    schema = program.final_output_schema or DEFAULT_FINAL_OUTPUT_SCHEMA
    sorted_rules = sorted(program.decision_rules, key=lambda r: r.priority)
    rendered_fields = "\n\n".join(_render_field(field) for field in program.computed_fields)
    rendered_rules = "\n".join(
        _render_rule(index, rule)
        for index, rule in enumerate(sorted_rules, start=1)
    )
    rendered_checks = "\n".join(_render_verifier(check) for check in program.verifier_checks)
    return f"""You are not explaining theory.
You are executing a decision program.

Game:
{program.game_id}

Mapped theory:
{program.theory_id}

Current state:
{state_summary}

Legal actions:
{json.dumps(program.legal_actions, ensure_ascii=False)}

Computed fields:
{rendered_fields}

Decision program:
P0. Choose only from legal_actions.
{rendered_rules}
P{len(sorted_rules) + 1}. If tied, use the listed tie-break rule if available; otherwise choose the first tied legal action.
P{len(sorted_rules) + 2}. Do not use unavailable fields as if they were computed.
P{len(sorted_rules) + 3}. Before final answer, run verifier checks.

Verifier:
{rendered_checks}

Return only valid JSON:
{json.dumps(schema, indent=2, ensure_ascii=False)}
"""
