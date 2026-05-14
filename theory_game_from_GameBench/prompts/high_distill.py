import json

from prompts.theory_fields import (
    format_theory_mapping_section,
    high_distill_output_schema,
    theory_mapping_for_game,
)


def build_high_distill_prompt(state):
    output_schema = high_distill_output_schema()
    mapping = theory_mapping_for_game(state.get("game_id"))
    active_context = state.get("prompt_context")
    theory_section = format_theory_mapping_section(
        mapping,
        distilled=True,
        active_context=active_context,
    )
    action_lines = []
    if state["predefined_actions_text"]:
        action_lines.append("Predefined actions:\n" + state["predefined_actions_text"])
    if state["openended_actions_text"]:
        action_lines.append("Openended actions:\n" + state["openended_actions_text"])

    prompt = f"""You are a strategic game-playing agent using high_distill compiled field program execution.

Game: {state['rules_title']}

Compiled field program execution:
{theory_section}

Rules summary:
{state['rules_summary']}

Additional rule details:
{state['rules_details_text'] or 'None'}

Observation:
{state['observation_text']}

Action instructions:
{state['action_instructions']}

Actions:
{chr(10).join(action_lines)}

Policy:
- Use the compiled field program above. Do not invent or redefine fields or program steps.
- Compute the field-register entries from the current observation in `field_application.computed_fields`.
- Use the Field computation targets as the reason each active field is needed for this current decision.
- Use the active role/action-space spec already selected in the prompt; do not switch to an unrelated role or program.
- `reference_basis_used` must copy exact labels from the Reference basis section, not field names.
- `field_application.active_action_space_program_used` must copy the active action-space program name from the prompt.
- `field_application.active_role_spec_used` must copy the active role-specific spec names from the prompt.
- `computed_fields` must include every base field name and every active role/action-space field name verbatim as JSON keys.
- If a required field is not observable, set that field's value to "unobserved" and also list the field name in `unavailable_fields`.
- Use only the current observation, available actions, rules, and reference basis. Do not add outside game rules or strategy-guide assumptions.
- Execute the compiled decision program step by step in `decision_program_trace`.
- Keep every computed field value and trace result to one compact phrase or short list.
- Include one trace entry per P0/P1/P2/P3-style rule, but do not expand every legal action unless the rule eliminates or selects it.
- Put the final program step that selected the action in `used_rule`.
- If the action is openended, provide the concrete response text required by the game.
- Never invent an unavailable action id.
- Output JSON only.

Return valid JSON with exactly this shape:
{json.dumps(output_schema, indent=2)}
"""
    return [
        {
            "role": "system",
            "content": "You are a compact strategic game agent. Return valid JSON only.",
        },
        {
            "role": "user",
            "content": prompt,
        },
    ]
