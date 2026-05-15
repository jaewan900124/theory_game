import json

from prompts.theory_fields import (
    field_register_for_prompt,
    high_reasoning_output_schema,
    theory_mapping_for_game,
)


ACTION_FORMAT_INSTRUCTIONS_NO_OPENENDED = """\
Return actions in json with the following keys.
{
    "action": str,
}
"""

ACTION_FORMAT_INSTRUCTIONS_WITH_OPENENDED = """\
Return actions in json with the following keys.
{
    "action": str,
    "openended_response": Optional[str],
}
Include the openended response only if you have chosen an openended action.
"""


def _base_actions_block(state):
    valid_actions = []
    lines = []
    if state["openended_actions"]:
        lines.append(ACTION_FORMAT_INSTRUCTIONS_WITH_OPENENDED.rstrip())
        lines.append("The following are openended actions you can take")
        lines.append(str(list(state["openended_actions"].keys())))
        valid_actions += list(state["openended_actions"])
    else:
        lines.append(ACTION_FORMAT_INSTRUCTIONS_NO_OPENENDED.rstrip())
    if state["predefined_actions"]:
        lines.append("The following are predefined actions you can take:")
        lines.append(str(list(state["predefined_actions"].keys())))
        valid_actions += list(state["predefined_actions"])
    if any(
        state["predefined_actions"].get(action) is not None
        or state["openended_actions"].get(action)
        for action in valid_actions
    ):
        lines.append(
            "Return the action Explain(<action>) to receive additional info about what any of the above actions do."
        )
    lines.extend(
        [
            "",
            "To summarize, if you choose a predefined action, you must return json with an 'action' key which contains one of the following valid actions:",
            str(list(state["predefined_actions"])),
            "Or if you choose an openended action, you must return json with an 'action' key which contains one of the following valid actions and an 'openended_response' key which contains your response to the prompt:",
            str(list(state["openended_actions"])),
            "Return valid JSON only.",
        ]
    )
    return "\n".join(lines)


def _field_register_block(field_register):
    return "\n".join(f"- {field}" for field in field_register)


def _field_rationale_extension(schema, field_register, include_analysis=True):
    analysis_rules = ""
    if include_analysis:
        analysis_rules = """\
- field_analysis must contain exactly one object per used field, in the same order.
- Each field_analysis object must have:
  - "field": one exact field name from used_fields
  - "value": a short phrase explaining how that field supports the action
- Keep each field_analysis.value short.
"""
    return f"""\

Additionally, include a compact field rationale in the same JSON object:
{json.dumps(schema, indent=2)}

# Field Register
{_field_register_block(field_register)}

# Field Selection Rule
Select 2 to 4 fields from the Field Register.
Prefer the smallest sufficient set of fields for the decision.
Use only fields that directly affect the chosen action; do not include fields that are only generally relevant.
Use 4 fields only when multiple competing factors materially affect the decision.

Additional rules:
- Keep the original base action interface: action must contain exactly one valid action id from the available actions.
- If the chosen action is openended, provide a concrete openended_response.
- If the chosen action is predefined, set openended_response to null.
- used_fields must contain 2 to 4 field names copied exactly from the Field Register.
{analysis_rules}- Return valid JSON only.
"""


def build_field_rationale_prompt(state, output_mode="compact"):
    output_schema = high_reasoning_output_schema()
    mapping = theory_mapping_for_game(state.get("game_id"))
    active_context = state.get("prompt_context")
    field_register = field_register_for_prompt(mapping, active_context)

    base_prompt = f"""You are playing a game called {state['rules_title']}. The rules are as follows:
{state['rules_summary']}
"""

    if state.get("rules_detail_headings"):
        base_prompt += (
            "The following are headings with additional information about "
            "the rules that you can expand by taking the action "
            "Explain(<heading key>).\n"
        )
        base_prompt += json.dumps(state["rules_detail_headings"], indent=4)

    base_prompt += f"""

# Observation
The following describes the current state of the game:
{state['observation_text']}

# Actions
{state['action_instructions']}
"""

    if output_mode == "debug":
        prompt = f"""{base_prompt}
{_base_actions_block(state)}

# Field Register
Use only fields from the following fixed field register:
{_field_register_block(field_register)}

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
            "action": "copy exactly one valid action id from the available actions",
            "openended_response": "concrete string when action is openended, otherwise null",
            "used_fields": [
                "copy 2 to 4 field names exactly from the field register"
            ],
        }
        prompt = f"""{base_prompt}
{_base_actions_block(state)}
{_field_rationale_extension(compact_schema, field_register, include_analysis=False)}
"""
    elif output_mode == "compact_field_analysis":
        compact_schema = {
            "action": "copy exactly one valid action id from the available actions",
            "openended_response": "concrete string when action is openended, otherwise null",
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
{_base_actions_block(state)}
{_field_rationale_extension(compact_schema, field_register, include_analysis=True)}
"""
    else:
        compact_schema = {
            "action": "copy exactly one valid action id from the available actions",
            "openended_response": "concrete string when action is openended, otherwise null",
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
{_base_actions_block(state)}
{_field_rationale_extension(compact_schema, field_register, include_analysis=True)}
"""

    return [
        {
            "role": "system",
            "content": "",
        },
        {
            "role": "user",
            "content": prompt,
        },
    ]
