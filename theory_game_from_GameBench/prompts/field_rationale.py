import json

from prompts.theory_fields import (
    field_register_for_prompt,
    high_reasoning_output_schema,
    theory_mapping_for_game,
)


def _baseline_actions_block(state, schema):
    lines = [
        "Return actions in json with the following keys.",
        json.dumps(schema, indent=2),
    ]
    if state["openended_actions"]:
        lines.append("The following are openended actions you can take")
        lines.append(str(list(state["openended_actions"].keys())))
    if state["predefined_actions"]:
        lines.append("The following are predefined actions you can take:")
        lines.append(str(list(state["predefined_actions"].keys())))
    if state["predefined_actions_text"] or state["openended_actions_text"]:
        lines.append(
            "Return the action Explain(<action>) to receive additional info about what any of the above actions do."
        )
    return "\n".join(lines)


def build_field_rationale_prompt(state, output_mode="compact"):
    output_schema = high_reasoning_output_schema()
    mapping = theory_mapping_for_game(state.get("game_id"))
    active_context = state.get("prompt_context")
    field_register = field_register_for_prompt(mapping, active_context)

    base_prompt = f"""You are playing a game called {state['rules_title']}. The rules are as follows:
{state['rules_summary']}

# Observation
The following describes the current state of the game:
{state['observation_text']}

# Actions
{state['action_instructions']}
"""

    if output_mode == "debug":
        prompt = f"""{base_prompt}
{_baseline_actions_block(state, output_schema)}

# Field Register
Use only fields from the following fixed field register:
{chr(10).join(f"- {field}" for field in field_register)}

Rules:
- Choose exactly one valid action id from the available actions.
- Compute field values only from the current observation, rules, and available actions.
- Do not invent or redefine fields.
- Include the required field_application object.
- If the chosen action is openended, provide a concrete openended_response.
- Return valid JSON only.
"""
    elif output_mode == "compact_basis":
        compact_schema = {
            "selected_action": "copy exactly one valid action id from the available actions",
            "openended_response": "concrete string when selected_action is openended, otherwise null",
            "used_fields": [
                "copy 2 to 4 field names exactly from the field register"
            ],
        }
        prompt = f"""{base_prompt}
{_baseline_actions_block(state, compact_schema)}

# Field Register
{chr(10).join(f"- {field}" for field in field_register)}

# Field Selection Rule
Select 2 to 4 fields from the Field Register.
Prefer the smallest sufficient set of fields for the decision.
Use only fields that directly affect the chosen action.
Do not include fields that are only generally relevant.
Use 4 fields only when multiple competing factors materially affect the decision.

Rules:
- Choose exactly one valid action id from the available actions.
- If the chosen action is openended, provide a concrete openended_response.
- used_fields must contain 2 to 4 field names copied exactly from the field register.
- Return valid JSON only.
"""
    elif output_mode == "compact_field_analysis":
        compact_schema = {
            "selected_action": "copy exactly one valid action id from the available actions",
            "openended_response": "concrete string when selected_action is openended, otherwise null",
            "used_fields": [
                "copy 2 to 4 field names exactly from the field register"
            ],
            "field_analysis": [
                {
                    "field": "one exact field name from used_fields",
                    "value": "short phrase explaining why that field supports the action",
                }
            ],
        }
        prompt = f"""{base_prompt}
{_baseline_actions_block(state, compact_schema)}

# Field Register
{chr(10).join(f"- {field}" for field in field_register)}

# Field Selection Rule
Select 2 to 4 fields from the Field Register.
Prefer the smallest sufficient set of fields for the decision.
Use only fields that directly affect the chosen action; do not include fields that are only generally relevant.
Use 4 fields only when multiple competing factors materially affect the decision.

Rules:
- selected_action must contain exactly one valid action id from the available actions.
- If the chosen action is openended, provide a concrete openended_response.
- If the chosen action is predefined, set openended_response to null.
- used_fields must contain 2 to 4 field names copied exactly from the Field Register.
- field_analysis must contain exactly one object per used field, in the same order.
- Each field_analysis object must have:
  - "field": one exact field name from used_fields
  - "value": a short phrase explaining how that field supports the selected action
- Keep each field_analysis.value short.
- Return valid JSON only.
"""
    else:
        compact_schema = {
            "selected_action": "copy exactly one valid action id from the available actions",
            "openended_response": "concrete string when selected_action is openended, otherwise null",
            "used_fields": [
                "copy 2 to 4 field names exactly from the field register"
            ],
            "field_analysis": [
                {
                    "field": "one exact field name from used_fields",
                    "value": "short phrase explaining why that field supports the action",
                }
            ],
        }
        prompt = f"""{base_prompt}
{_baseline_actions_block(state, compact_schema)}

# Field Register
{chr(10).join(f"- {field}" for field in field_register)}

# Field Selection Rule
Select 2 to 4 fields from the Field Register.
Prefer the smallest sufficient set of fields for the decision.
Use only fields that directly affect the chosen action.
Do not include fields that are only generally relevant.
Use 4 fields only when multiple competing factors materially affect the decision.

Rules:
- Choose exactly one valid action id from the available actions.
- selected_action must be exactly one valid action id from the available actions.
- If the chosen action is openended, provide a concrete openended_response.
- used_fields must contain 2 to 4 field names copied exactly from the field register.
- field_analysis must contain exactly one object per used field, in the same order.
- Each field_analysis object must have:
  - "field": one exact field name from used_fields
  - "value": a short phrase explaining how that field supports the selected action
- Keep each field_analysis.value short.
- Return valid JSON only.
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
