import re


def get_valid_evidence_ids(evidence_items):
    valid_ids = set()

    for item in evidence_items:
        valid_ids.add(f"chunk_{item.get('chunk_id')}")

    return valid_ids


def validate_recommendation(answer, evidence_items):
    valid_ids = get_valid_evidence_ids(evidence_items)
    used_ids = set(re.findall(r"chunk_\d+", answer))

    invalid_ids = used_ids - valid_ids

    checks = {
        "has_answer": bool(answer.strip()),
        "has_evidence": len(evidence_items) > 0,
        "uses_valid_evidence_ids": len(invalid_ids) == 0,
        "mentions_recommendation": "recommendation" in answer.lower() or "action" in answer.lower(),
        "mentions_risk": "risk" in answer.lower(),
        "mentions_priority": "priority" in answer.lower(),
        "mentions_confidence": "confidence" in answer.lower(),
    }

    passed = all(checks.values())

    issues = []

    for check_name, status in checks.items():
        if not status:
            issues.append(check_name)

    return {
        "tool_name": "validate_recommendation_tool",
        "passed": passed,
        "checks": checks,
        "used_evidence_ids": sorted(list(used_ids)),
        "valid_evidence_ids": sorted(list(valid_ids)),
        "invalid_evidence_ids": sorted(list(invalid_ids)),
        "issues": issues,
    }