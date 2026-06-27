def detect_goal_type(goal):
    goal_lower = goal.lower()

    strategic_words = [
        "prioritize",
        "recommend",
        "recommendation",
        "strategic action",
        "what should",
        "next",
        "decide",
        "decision",
        "management should",
        "ceo",
    ]

    if any(word in goal_lower for word in strategic_words):
        return "strategic_decision"

    if any(word in goal_lower for word in ["risk", "threat", "challenge", "problem"]):
        return "risk_analysis"

    if any(word in goal_lower for word in ["opportunity", "growth", "expand", "improve"]):
        return "opportunity_analysis"

    if any(word in goal_lower for word in ["trend", "market", "recent", "future"]):
        return "trend_analysis"

    if any(word in goal_lower for word in ["competitor", "competition", "oracle", "microsoft", "salesforce"]):
        return "competitor_analysis"

    return "strategic_decision"


def create_agent_plan(goal):
    goal_type = detect_goal_type(goal)

    analysis_tools = []

    if goal_type == "risk_analysis":
        analysis_tools = ["analyze_risks_tool", "analyze_trends_tool"]

    elif goal_type == "opportunity_analysis":
        analysis_tools = ["analyze_opportunities_tool", "analyze_trends_tool", "analyze_risks_tool"]

    elif goal_type == "trend_analysis":
        analysis_tools = ["analyze_trends_tool", "analyze_opportunities_tool", "analyze_risks_tool"]

    elif goal_type == "competitor_analysis":
        analysis_tools = ["analyze_trends_tool", "analyze_risks_tool"]

    else:
        analysis_tools = ["analyze_opportunities_tool", "analyze_risks_tool", "analyze_trends_tool"]

    plan = {
        "goal": goal,
        "goal_type": goal_type,
        "steps": [
            "Understand the CEO goal",
            "Create an execution plan",
            "Select analysis tools",
            "Retrieve evidence from vector memory",
            "Analyze risks, opportunities, and trends",
            "Generate recommendation",
            "Validate recommendation against evidence",
            "Store agent run in memory",
        ],
        "tools": [
            "retrieve_evidence_tool",
            *analysis_tools,
            "generate_recommendation_tool",
            "validate_recommendation_tool",
            "save_agent_memory_tool",
        ],
        "analysis_tools": analysis_tools,
    }

    return plan