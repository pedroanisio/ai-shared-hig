import json
import re
from pathlib import Path

import pytest


P5_PATH = Path(__file__).resolve().parents[1] / "data/master_data/patterns_json/P5.json"

UNICODE_OPERATORS = {
    "\u2265": ">=",
    "\u2264": "<=",
    "\u00ac": "not ",
    "\u2227": " and ",
    "\u2228": " or ",
}


def load_applicability():
    with P5_PATH.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return data["applicability"]


def load_p5():
    with P5_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def find_component(p5, name):
    for comp in p5.get("comps", []):
        if comp.get("n") == name:
            return comp
    return None


def find_type(p5, name):
    for typedef in p5.get("types", []):
        if typedef.get("n") == name:
            return typedef
    return None


def parse_record_fields(definition):
    match = re.match(r"^\((.*)\)$", definition.strip())
    if not match:
        return set()
    inner = match.group(1)
    fields = []
    for chunk in inner.split(","):
        chunk = chunk.strip()
        if ":" in chunk:
            fields.append(chunk.split(":", 1)[0].strip())
    return set(fields)


def normalize_expr(expr):
    for src, dst in UNICODE_OPERATORS.items():
        expr = expr.replace(src, dst)
    expr = re.sub(r"(?<![<>=!])=(?!=)", "==", expr)
    return expr


def eval_expr(expr, ctx):
    expr = normalize_expr(expr)
    return eval(expr, {"__builtins__": {}}, dict(ctx))


def evaluate_applicability(spec, ctx):
    predicates = list(spec["predicates"].values())
    total_weight = sum(p["weight"] for p in predicates)
    score = sum(
        p["weight"] for p in predicates if eval_expr(p["def"], ctx)
    ) / total_weight
    contraindications = [
        c for c in spec.get("contraindications", [])
        if eval_expr(c["condition"], ctx)
    ]
    hard_fail = any(c["severity"] == "hard" for c in contraindications)
    required_fail = any(
        p.get("required") and not eval_expr(p["def"], ctx)
        for p in predicates
    )
    applicable = (not hard_fail) and (not required_fail) and score >= spec["scoring"]["threshold"]
    return score, applicable, contraindications


def test_p5_applicability_all_predicates():
    spec = load_applicability()
    ctx = {
        "n_items": 4,
        "item_independence": 0.8,
        "state_weight": 2048,
        "switch_frequency": 1.0,
        "viewport_width": 1024,
        "comparison_need": 0.1,
        "sequential_flow": False,
        "max_concurrent": 3,
    }
    score, applicable, contraindications = evaluate_applicability(spec, ctx)
    assert score == pytest.approx(1.0)
    assert applicable is True
    assert contraindications == []


def test_p5_applicability_partial_score_still_passes():
    spec = load_applicability()
    ctx = {
        "n_items": 3,
        "item_independence": 0.6,
        "state_weight": 900,
        "switch_frequency": 0.4,
        "viewport_width": 800,
        "comparison_need": 0.2,
        "sequential_flow": False,
        "max_concurrent": 2,
    }
    score, applicable, _ = evaluate_applicability(spec, ctx)
    assert score == pytest.approx(3.6 / 5.7, rel=1e-3)
    assert applicable is True


def test_p5_applicability_required_or_hard_failure():
    spec = load_applicability()
    ctx_required_fail = {
        "n_items": 2,
        "item_independence": 0.9,
        "state_weight": 2048,
        "switch_frequency": 1.0,
        "viewport_width": 600,
        "comparison_need": 0.1,
        "sequential_flow": False,
        "max_concurrent": 3,
    }
    score, applicable, contraindications = evaluate_applicability(spec, ctx_required_fail)
    assert score < 1.0
    assert applicable is False
    assert contraindications == []

    ctx_hard_fail = {
        "n_items": 1,
        "item_independence": 0.8,
        "state_weight": 2048,
        "switch_frequency": 1.0,
        "viewport_width": 1024,
        "comparison_need": 0.1,
        "sequential_flow": False,
        "max_concurrent": 1,
    }
    _, applicable, contraindications = evaluate_applicability(spec, ctx_hard_fail)
    assert applicable is False
    assert any(c["id"] == "C1" for c in contraindications)


def test_p5_tab_semantics_are_consistent():
    p5 = load_p5()
    tabs = find_component(p5, "tabs")
    assert tabs, "tabs component missing"
    tabs_type = tabs.get("t", "")

    ops_text = " ".join(op.get("def", "") for op in p5.get("ops", []))
    if "Sequence" in tabs_type:
        assert "∪" not in ops_text, "sequence tabs should not use set union"
        assert "\\\\" not in ops_text, "sequence tabs should not use set difference"
        assert "tab_id ∈ tabs" not in ops_text, "sequence tabs should not use set membership by id"
        assert "tabs[tab_id]" not in ops_text, "sequence tabs should not be indexed by id"


def test_p5_tab_type_matches_operations():
    p5 = load_p5()
    tab_type = find_type(p5, "Tab")
    assert tab_type, "Tab type missing"
    fields = parse_record_fields(tab_type.get("def", ""))
    ops_text = " ".join(op.get("def", "") for op in p5.get("ops", []))
    if "tab.item" in ops_text or "Tab(item)" in ops_text:
        assert "item" in fields, "Tab type must include item if operations use tab.item or Tab(item)"


def test_p5_active_type_matches_usage():
    p5 = load_p5()
    active = find_component(p5, "active")
    assert active, "active component missing"
    active_type = active.get("t", "")
    ops_text = " ".join(op.get("def", "") for op in p5.get("ops", []))
    if active_type.strip() == "ℕ":
        assert "active_tab" not in ops_text, "active is an index but ops reference active_tab id"


def test_p5_applicability_types_present():
    p5 = load_p5()
    app_types = find_type(p5, "ApplicabilityResult")
    assert app_types, "ApplicabilityResult type missing"
    type_names = {typedef.get("n") for typedef in p5.get("types", [])}
    if "Contraindication" in app_types.get("def", ""):
        assert "Contraindication" in type_names, "Contraindication type missing"
    if "Pattern" in app_types.get("def", ""):
        assert "Pattern" in type_names, "Pattern type missing"


def test_p5_predicates_have_ids_when_used():
    p5 = load_p5()
    eval_op = next((op for op in p5.get("ops", []) if op.get("n") == "Evaluate Applicability"), None)
    assert eval_op, "Evaluate Applicability op missing"
    if "p.id" in eval_op.get("def", ""):
        predicates = p5.get("applicability", {}).get("predicates", {})
        for key, predicate in predicates.items():
            assert "id" in predicate, f"predicate '{key}' missing id"
