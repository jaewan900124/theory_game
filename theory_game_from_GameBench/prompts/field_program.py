import json

from prompts.theory_fields import (
    program_for_prompt,
    theory_mapping_for_game,
    verifier_checks_for_prompt,
)


def build_field_program_prompt(state, output_mode="compact"):
    mapping = theory_mapping_for_game(state.get("game_id"))
    active_context = state.get("prompt_context")
    program_rules = program_for_prompt(mapping, active_context)
    verifier_checks = verifier_checks_for_prompt(mapping, active_context)

    action_notes = []
    if state["predefined_actions_text"]:
        action_notes.append("Predefined actions:\n" + state["predefined_actions_text"])
    if state["openended_actions_text"]:
        action_notes.append("Openended actions:\n" + state["openended_actions_text"])

    base_prompt = f"""You are playing a game called {state['rules_title']}. The rules are as follows:
{state['rules_summary']}

# Observation
The following describes the current state of the game:
{state['observation_text']}

# Actions
{state['action_instructions']}
"""

    if output_mode == "debug":
        debug_schema = {
            "selected_action": "copy exactly one valid action id from the available actions",
            "openended_response": "concrete string when selected_action is openended, otherwise null",
            "used_rule": "copy the final program rule label most responsible for the selection",
            "rule_analysis": [
                {
                    "rule": "same rule label as used_rule",
                    "value": "short phrase explaining why that rule selected this action",
                }
            ],
            "decision_trace": [
                {
                    "step": "P1/P2/etc.",
                    "result": "short phrase describing the filtering or comparison outcome",
                }
            ],
        }
        prompt = f"""{base_prompt}
Return actions in json with the following keys.
{json.dumps(debug_schema, indent=2)}

The following are available actions:
{chr(10).join(action_notes)}

# Decision Program
- P0. Choose only from the current available action ids.
{chr(10).join(f"- {rule}" for rule in program_rules)}
- P*. If multiple actions remain tied, choose the strongest legal best-response action.

# Verifier Checks
{chr(10).join(f"- {check}" for check in verifier_checks)}

Rules:
- Choose exactly one valid action id from the available actions.
- If the chosen action is openended, provide a concrete openended_response.
- Execute the decision program step by step using only the current observation, rules, and available actions.
- Do not invent unavailable action ids or unsupported rule steps.
- Return valid JSON only.
"""
    elif output_mode == "compact_basis":
        compact_schema = {
            "selected_action": "copy exactly one valid action id from the available actions",
            "openended_response": "concrete string when selected_action is openended, otherwise null",
            "used_rule": "copy the final program rule label most responsible for the selection",
        }
        prompt = f"""{base_prompt}
Return actions in json with the following keys.
{json.dumps(compact_schema, indent=2)}

The following are available actions:
{chr(10).join(action_notes)}

# Decision Program
- P0. Choose only from the current available action ids.
{chr(10).join(f"- {rule}" for rule in program_rules)}
- P*. If multiple actions remain tied, choose the strongest legal best-response action.

# Verifier Checks
{chr(10).join(f"- {check}" for check in verifier_checks)}

Rules:
- Choose exactly one valid action id from the available actions.
- If the chosen action is openended, provide a concrete openended_response.
- used_rule must copy the final program rule that most directly selected the action.
- Return valid JSON only.
"""
    elif output_mode == "compact_field_analysis":
        compact_schema = {
            "selected_action": "copy exactly one valid action id from the available actions",
            "openended_response": "concrete string when selected_action is openended, otherwise null",
            "used_rule": "copy the final program rule label most responsible for the selection",
            "rule_analysis": [
                {
                    "rule": "same rule label as used_rule",
                    "value": "short phrase explaining why that rule selected this action",
                }
            ],
        }
        prompt = f"""{base_prompt}
Return actions in json with the following keys.
{json.dumps(compact_schema, indent=2)}

The following are available actions:
{chr(10).join(action_notes)}

# Decision Program
- P0. Choose only from the current available action ids.
{chr(10).join(f"- {rule}" for rule in program_rules)}
- P*. If multiple actions remain tied, choose the strongest legal best-response action.

# Verifier Checks
{chr(10).join(f"- {check}" for check in verifier_checks)}

Rules:
- Choose exactly one valid action id from the available actions.
- selected_action must be exactly one valid action id from the available actions.
- If the chosen action is openended, provide a concrete openended_response.
- used_rule must copy the final program rule that most directly selected the action.
- rule_analysis must contain exactly one object for used_rule.
- Each rule_analysis object must have:
  - "rule": the same rule label as used_rule
  - "value": a short phrase explaining why that rule selected the action
- Keep each rule_analysis.value short.
- Return valid JSON only.
"""
    else:
        compact_schema = {
            "selected_action": "copy exactly one valid action id from the available actions",
            "openended_response": "concrete string when selected_action is openended, otherwise null",
            "used_rule": "copy the final program rule label most responsible for the selection",
        }
        prompt = f"""{base_prompt}
Return actions in json with the following keys.
{json.dumps(compact_schema, indent=2)}

The following are available actions:
{chr(10).join(action_notes)}

# Decision Program
- P0. Choose only from the current available action ids.
{chr(10).join(f"- {rule}" for rule in program_rules)}
- P*. If multiple actions remain tied, choose the strongest legal best-response action.

# Verifier Checks
{chr(10).join(f"- {check}" for check in verifier_checks)}

Rules:
- Choose exactly one valid action id from the available actions.
- If the chosen action is openended, provide a concrete openended_response.
- used_rule must copy the final program rule that most directly selected the action.
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
