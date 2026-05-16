import json

from prompts.theory_fields import (
    format_theory_mapping_section,
    high_reasoning_output_schema,
    theory_mapping_for_game,
)


def build_high_reasoning_prompt(state, output_mode="compact"):
    profile = state.get("profile", {})
    output_schema = high_reasoning_output_schema()
    mapping = theory_mapping_for_game(state.get("game_id"))
    active_context = state.get("prompt_context")
    theory_section = format_theory_mapping_section(
        mapping,
        distilled=False,
        active_context=active_context,
    )
    action_notes = []
    if state["predefined_actions_text"]:
        action_notes.append("Predefined actions:\n" + state["predefined_actions_text"])
    if state["openended_actions_text"]:
        action_notes.append("Openended actions:\n" + state["openended_actions_text"])
    profile_style = profile.get("style", "general strategic reasoning")
    openended_examples = profile.get("openended_examples", {})
    example_text = ""
    if openended_examples:
        example_text = "\nOpenended response examples:\n" + "\n".join(
            f"- {action}: {example}" for action, example in openended_examples.items()
        )

    base_prompt = f"""You are a strategic game-playing agent using high_reasoning engineered field reasoning.

Game: {state['rules_title']}
Strategic style: {profile_style}

Engineered field reasoning:
{theory_section}

Rules summary:
{state['rules_summary']}

Additional rule details:
{state['rules_details_text'] or 'None'}

Current observation:
{state['observation_text']}

Action instructions:
{state['action_instructions']}

Available actions:
{chr(10).join(action_notes)}
{example_text}
"""

    if output_mode == "debug":
        prompt = f"""{base_prompt}
Use the engineered field register above. Do not invent or redefine fields.
Output JSON only.
Requirements:
- Compute the field-register entries from the current observation in `field_application.computed_fields`.
- Use the Field computation targets as the reason each active field is needed for this current decision.
- Use the active role/action-space spec already selected in the prompt; do not switch to an unrelated role or program.
- `reference_basis_used` must copy exact labels from the Reference basis section, not field names.
- `field_application.active_action_space_program_used` must copy the active action-space program name from the prompt.
- `field_application.active_role_spec_used` must copy the active role-specific spec names from the prompt.
- `computed_fields` must include every base field name and every active role/action-space field name verbatim as JSON keys.
- If a required field is not observable, set that field's value to "unobserved" and also list the field name in `unavailable_fields`.
- Use only the current observation, available actions, rules, and reference basis. Do not add outside game rules or strategy-guide assumptions.
- This high_reasoning variant does not receive a compiled decision program. Use the computed fields to reason over legal actions yourself.
- Keep every computed field value to one compact phrase or short list.
- Compare only the 2-3 strongest legal candidate actions in `candidate_action_values`.
- Choose exactly one action id copied from the available actions.
- If the chosen action is openended, provide a concrete `openended_response`.
- Never invent an unavailable action.
- Run the verifier checks before returning the final JSON.

Return valid JSON with exactly this shape:
{json.dumps(output_schema, indent=2)}
"""
    elif output_mode == "compact_basis":
        compact_schema = {
            "selected_action": "copy exactly one valid action id from the available actions",
            "openended_response": "concrete string when selected_action is openended, otherwise null",
            "used_fields": [
                "copy 1 to 3 field names from the field register that most directly supported the selected action"
            ],
        }
        prompt = f"""{base_prompt}
Use the engineered field register above internally. Do not invent or redefine fields.
Use only the current observation, available actions, rules, and reference basis.
Choose exactly one action id copied from the available actions.
If the chosen action is openended, provide a concrete openended_response.
Set used_fields to 1 to 3 exact field names from the field register that most directly supported the selected action.
Run the verifier checks before returning the final JSON, but do not expand them in the output.
Return only the final action JSON with the three schema keys below and no other keys or text.

Return valid JSON with exactly this shape:
{json.dumps(compact_schema, indent=2)}
"""
    elif output_mode == "compact_field_analysis":
        compact_schema = {
            "selected_action": "copy exactly one valid action id from the available actions",
            "openended_response": "concrete string when selected_action is openended, otherwise null",
            "used_fields": [
                "copy 1 to 2 field names from the field register that most directly supported the selected action"
            ],
            "field_analysis": [
                {
                    "field": "one exact field name from used_fields",
                    "value": "short phrase, maximum 30 words, computed for this decision",
                }
            ],
        }
        prompt = f"""{base_prompt}
Use the engineered field register above internally. Do not invent or redefine fields.
Use only the current observation, available actions, rules, and reference basis.
Choose exactly one action id copied from the available actions.
selected_action must be exactly one action id from the Available actions list.
Do not append explanations, coordinates, punctuation, or action descriptions to selected_action.
If the chosen action is openended, provide a concrete openended_response.
If the chosen openended action is STOP, openended_response must be a valid STOP command string such as ["STOP", ""] or ["STOP", []], matching the action instructions.
Set used_fields to 1 to 2 exact field names from the field register that most directly supported the selected action.
Include field_analysis with exactly one object per used_fields entry, in the same order.
Keep every field_analysis.value to a short phrase, maximum 30 words.
Put any short rationale only in field_analysis.value.
Run the verifier checks before returning the final JSON, but do not expand them in the output.
Return only the final action JSON with the four schema keys below and no other keys or text.

Return valid JSON with exactly this shape:
{json.dumps(compact_schema, indent=2)}
"""
    else:
        compact_schema = {
            "selected_action": "copy exactly one valid action id from the available actions",
            "openended_response": "concrete string when selected_action is openended, otherwise null",
        }
        prompt = f"""{base_prompt}
Use the engineered field register above internally. Do not invent or redefine fields.
Use only the current observation, available actions, rules, and reference basis.
Choose exactly one action id copied from the available actions.
If the chosen action is openended, provide a concrete openended_response.
Return only the final action JSON with the two schema keys below and no other keys or text.

Return valid JSON with exactly this shape:
{json.dumps(compact_schema, indent=2)}
"""
    return [
        {
            "role": "system",
            "content": "You are a precise strategic game agent. Return valid JSON only.",
        },
        {
            "role": "user",
            "content": prompt,
        },
    ]
