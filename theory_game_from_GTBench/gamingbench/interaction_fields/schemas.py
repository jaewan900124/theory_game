from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


UNAVAILABLE_STATUS = "unavailable"


def unavailable(reason: str) -> Dict[str, str]:
    return {"status": UNAVAILABLE_STATUS, "reason": reason}


def is_unavailable(value: Any) -> bool:
    return isinstance(value, dict) and value.get("status") == UNAVAILABLE_STATUS


@dataclass
class InteractionFieldSpec:
    field_id: str
    source_game_id: str
    source_theory_id: str
    description: str
    raw_inputs: List[str]
    requirements: List[str]
    calculation: Dict[str, Any]
    output_type: str
    value: Any
    decision_role: str
    priority: Optional[int]
    operator: str
    invariants: List[str]
    failure_mode_if_ignored: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DecisionRule:
    rule_id: str
    priority: int
    field_id: str
    operator: str
    action: str
    description: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class VerifierCheck:
    check_id: str
    field_id: Optional[str]
    condition: str
    expected: Any

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CompiledDecisionProgram:
    game_id: str
    theory_id: str
    current_player: Optional[str]
    legal_actions: List[str]
    computed_fields: List[InteractionFieldSpec]
    decision_rules: List[DecisionRule]
    tie_break_rules: List[DecisionRule] = field(default_factory=list)
    verifier_checks: List[VerifierCheck] = field(default_factory=list)
    final_output_schema: Dict[str, Any] = field(default_factory=dict)
    small_model_prompt: str = ""

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["computed_fields"] = [item.to_dict() for item in self.computed_fields]
        data["decision_rules"] = [item.to_dict() for item in self.decision_rules]
        data["tie_break_rules"] = [item.to_dict() for item in self.tie_break_rules]
        data["verifier_checks"] = [item.to_dict() for item in self.verifier_checks]
        return data
