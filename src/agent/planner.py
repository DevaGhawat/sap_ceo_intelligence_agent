def detect_goal_type(goal):
    goal_text = goal.lower()

    risk_keywords = [
        "risk",
        "risks",
        "challenge",
        "challenges",
        "barrier",
        "barriers",
        "threat",
        "threats",
        "concern",
        "concerns",
        "limit",
        "limits",
        "limiting",
        "reduce those risks",
        "reduce risks",
        "mitigate",
        "mitigation",
        "adoption risk",
        "compliance",
        "governance",
        "privacy",
        "security",
        "trust",
        "auditability",
        "uncertainty",
        "data quality",
        "fragmented data",
        "integration complexity",
    ]

    trend_keywords = [
        "trend",
        "trends",
        "monitor",
        "watch",
        "market direction",
        "future direction",
        "emerging",
        "shift",
        "shifts",
        "next 12 months",
        "over the next",
        "cloud trends",
        "enterprise ai and cloud trends",
    ]

    competitor_keywords = [
        "competitor",
        "competitors",
        "competition",
        "competitive",
        "rival",
        "rivals",
        "market share",
        "microsoft",
        "oracle",
        "salesforce",
        "workday",
    ]

    opportunity_keywords = [
        "opportunity",
        "opportunities",
        "growth",
        "expand",
        "expansion",
        "partnership",
        "partnerships",
        "new market",
        "customer adoption",
        "increase adoption",
        "revenue growth",
        "strongest growth",
    ]

    # Priority matters.
    # Specific analytical goals should be detected before generic strategy wording.
    if any(keyword in goal_text for keyword in risk_keywords):
        return "risk_analysis"

    if any(keyword in goal_text for keyword in trend_keywords):
        return "trend_analysis"

    if any(keyword in goal_text for keyword in competitor_keywords):
        return "competitor_analysis"

    if any(keyword in goal_text for keyword in opportunity_keywords):
        return "opportunity_analysis"

    return "strategic_decision"


def create_agent_plan(goal):
    goal_type = detect_goal_type(goal)

    base_steps = [
        "Understand the CEO goal",
        "Create an execution plan",
        "Select analysis tools",
        "Retrieve evidence from vector memory",
    ]

    if goal_type == "risk_analysis":
        analysis_steps = [
            "Analyze adoption risks, barriers, governance issues, and enterprise challenges",
            "Analyze trend signals that may increase or reduce risk",
        ]
        analysis_tools = [
            "analyze_risks_tool",
            "analyze_trends_tool",
        ]

    elif goal_type == "opportunity_analysis":
        analysis_steps = [
            "Analyze growth opportunities, adoption signals, partnerships, and market expansion areas",
            "Analyze trend signals that support future growth",
        ]
        analysis_tools = [
            "analyze_opportunities_tool",
            "analyze_trends_tool",
        ]

    elif goal_type == "trend_analysis":
        analysis_steps = [
            "Analyze enterprise AI, cloud, product, and market trend signals",
        ]
        analysis_tools = [
            "analyze_trends_tool",
        ]

    elif goal_type == "competitor_analysis":
        analysis_steps = [
            "Analyze competitive pressure and market positioning signals",
            "Analyze risks and opportunities created by competitors",
        ]
        analysis_tools = [
            "analyze_risks_tool",
            "analyze_opportunities_tool",
        ]

    else:
        analysis_steps = [
            "Analyze risks, opportunities, and trends",
        ]
        analysis_tools = [
            "analyze_opportunities_tool",
            "analyze_risks_tool",
            "analyze_trends_tool",
        ]

    final_steps = [
        "Generate recommendation",
        "Validate recommendation against evidence",
        "Store agent run in memory",
    ]

    tools = [
        "retrieve_evidence_tool",
        *analysis_tools,
        "generate_recommendation_tool",
        "validate_recommendation_tool",
        "save_agent_memory_tool",
    ]

    return {
        "goal": goal,
        "goal_type": goal_type,
        "steps": base_steps + analysis_steps + final_steps,
        "analysis_tools": analysis_tools,
        "tools": tools,
    }
    