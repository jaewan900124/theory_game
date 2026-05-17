import json

from agents.trace_utils import format_action_id_reference
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


def _base_actions_block(state, include_action_id_reference=False):
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
    if include_action_id_reference:
        action_reference = format_action_id_reference(
            state["predefined_actions"],
            state["openended_actions"],
            game_id=state.get("game_id"),
            observation_text=state.get("observation_text", ""),
            action_instructions=state.get("action_instructions", ""),
        )
        if action_reference:
            lines.extend(["", action_reference])
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


def _actions_block(state, pre_output_block="", include_action_id_reference=False):
    lines = [
        "# Actions",
        state["action_instructions"],
    ]
    if pre_output_block:
        lines.extend(["", pre_output_block.strip()])
    lines.extend(["", _base_actions_block(state, include_action_id_reference)])
    return "\n".join(lines)


def _field_register_block(field_register):
    return "\n".join(f"- {field}" for field in field_register)


def _field_rationale_extension(extra_schema, field_register, include_analysis=True):
    analysis_rules = ""
    if include_analysis:
        analysis_rules = """\
- field_analysis must contain exactly one object per used field, in the same order.
- Each field_analysis object must have:
  - "field": one exact field name from used_fields
  - "value": one concise sentence, up to 30 words, naming the concrete words, risks, counts, or clue links computed for this field
"""
    return f"""\

Additional decision support:
Use the Field Register as a compact checklist for selecting the action.
Do not treat the fields as additional game rules or extra available actions.

# Field Register
{_field_register_block(field_register)}

# Field Selection Rule
Select 2 to 6 fields from the Field Register.
Prefer the smallest sufficient set of fields for the decision.
Use only fields that directly affect the chosen action; do not include fields that are only generally relevant.
Use more than 5 fields only when multiple competing factors materially affect the decision.
Only bullet names listed under # Field Register are valid field names.
Do not put output key names such as action, used_fields, field_analysis, or openended_response inside used_fields.

Return the original action fields required below, and also include these additional fields.
These key names are not Field Register fields:
{json.dumps(extra_schema, indent=2)}

Rules:
- used_fields must contain 2 to 6 field names copied exactly from the Field Register.
{analysis_rules}
"""


def build_field_rationale_prompt(
    state,
    output_mode="compact",
    include_action_id_reference=False,
):
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
"""

    if output_mode == "debug":
        extra_schema = {
            "used_fields": [
                "2 to 6 field names copied exactly from the Field Register"
            ],
            "field_analysis": [
                {
                    "field": "one exact field name from used_fields",
                    "value": "one concise sentence, up to 30 words, naming the concrete words, risks, counts, or clue links computed for this field",
                }
            ],
            "field_application": {
                "selected_action": "same valid action id as action",
                "candidate_action_values": [
                    {
                        "action": "valid action id considered",
                        "value": "brief value, risk, or tradeoff computed from the selected fields",
                    }
                ],
                "selection_rationale": "brief explanation of why the selected action has the best value under the selected fields",
            },
        }
        prompt = f"""{base_prompt}
{_actions_block(
    state,
    f'''# Field Register
Use only fields from the following fixed field register:
{_field_register_block(field_register)}

# Full Field Application
Return the original action fields required below, and also include these additional fields.
These key names are not Field Register fields:
{json.dumps(extra_schema, indent=2)}

Rules:
- Choose exactly one valid action id from the available actions.
- used_fields must contain 2 to 6 field names copied exactly from the Field Register.
- Do not put output key names such as action, used_fields, field_analysis, field_application, or openended_response inside used_fields.
- field_analysis must contain exactly one object per used field, in the same order.
- Each field_analysis value must be one concise sentence, up to 30 words.
- field_application.selected_action must exactly match action.
- candidate_action_values should compare the strongest plausible legal actions when there is a real choice.
- Compute field values only from the current observation, rules, and available actions.
- Do not invent or redefine fields.
- Include the required field_application object.
- If the chosen action is openended, provide a concrete openended_response.
''',
    include_action_id_reference=include_action_id_reference,
)}
"""
    elif output_mode == "compact_basis":
        extra_schema = {
            "used_fields": [
                "2 to 6 field names copied exactly from the Field Register"
            ],
        }
        prompt = f"""{base_prompt}
{_actions_block(
    state,
    _field_rationale_extension(extra_schema, field_register, include_analysis=False),
    include_action_id_reference=include_action_id_reference,
)}
"""
    elif output_mode == "compact_field_analysis":
        extra_schema = {
            "used_fields": [
                "2 to 6 field names copied exactly from the Field Register"
            ],
            "field_analysis": [
                {
                    "field": "one exact field name from used_fields",
                    "value": "one concise sentence, up to 30 words, naming the concrete words, risks, counts, or clue links computed for this field",
                }
            ],
        }
        prompt = f"""{base_prompt}
{_actions_block(
    state,
    _field_rationale_extension(extra_schema, field_register, include_analysis=True),
    include_action_id_reference=include_action_id_reference,
)}
"""
    else:
        extra_schema = {
            "used_fields": [
                "2 to 6 field names copied exactly from the Field Register"
            ],
            "field_analysis": [
                {
                    "field": "one exact field name from used_fields",
                    "value": "one concise sentence, up to 30 words, naming the concrete words, risks, counts, or clue links computed for this field",
                }
            ],
        }
        prompt = f"""{base_prompt}
{_actions_block(
    state,
    _field_rationale_extension(extra_schema, field_register, include_analysis=True),
    include_action_id_reference=include_action_id_reference,
)}
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
