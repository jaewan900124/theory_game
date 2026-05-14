from gamingbench.agents.prompt_agent import PromptAgent


def test_json_final_decision_selected_action_has_priority_over_legal_actions_list():
    response = """
{
  "state_reconstruction": {
    "legal_actions": ["<C1R3>", "<C2R3>"]
  },
  "final_decision": {
    "selected_action": "<C2R3>",
    "action_source": "immediate_block",
    "confidence": "high"
  }
}
"""
    assert PromptAgent._legal_move_from_response_text(
        [response], ["<C1R3>", "<C2R3>"]) == "<C2R3>"


def test_json_fenced_response_is_supported():
    response = """```json
{"final_decision": {"selected_action": "<C2R2>"}}
```"""
    assert PromptAgent._legal_move_from_response_text(
        [response], ["<C1R1>", "<C2R2>"]) == "<C2R2>"


def test_json_decision_selected_action_is_supported_for_program_prompt():
    response = """
{
  "decision": {
    "selected_action": "<roll>",
    "reason_code": "roll_at_zero",
    "confidence": "high"
  }
}
"""
    assert PromptAgent._legal_move_from_response_text(
        [response], ["<roll>", "<stop>"]) == "<roll>"


def test_action_marker_remains_supported_for_non_json_responses():
    response = "Reasoning omitted.\nAction:\n<C3R1>"
    assert PromptAgent._legal_move_from_response_text(
        [response], ["<C1R1>", "<C3R1>"]) == "<C3R1>"


def test_plain_text_fallback_remains_supported():
    response = "I choose <C1R1>."
    assert PromptAgent._legal_move_from_response_text(
        [response], ["<C1R1>", "<C3R1>"]) == "<C1R1>"
