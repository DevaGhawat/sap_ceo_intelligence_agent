from src.agent.memory import load_recent_agent_runs, save_agent_run
from src.agent.planner import create_agent_plan
from src.agent.tools import (
    analyze_opportunities_tool,
    analyze_risks_tool,
    analyze_trends_tool,
    generate_recommendation_tool,
    retrieve_evidence_tool,
)
from src.agent.validator import validate_recommendation


ANALYSIS_TOOL_MAP = {
    "analyze_risks_tool": analyze_risks_tool,
    "analyze_opportunities_tool": analyze_opportunities_tool,
    "analyze_trends_tool": analyze_trends_tool,
}


def run_ceo_agent(goal):
    if not goal.strip():
        return {
            "answer": "No goal was provided.",
            "evidence_items": [],
            "agent_plan": {},
            "execution_trace": [],
            "validation": {},
        }

    execution_trace = []

    recent_memory = load_recent_agent_runs(limit=3)

    execution_trace.append(
        {
            "step": "Goal received",
            "details": goal,
        }
    )

    plan = create_agent_plan(goal)

    execution_trace.append(
        {
            "step": "Plan created",
            "details": f"Goal type detected: {plan['goal_type']}",
        }
    )

    evidence_result = retrieve_evidence_tool(goal)
    evidence_items = evidence_result["evidence_items"]

    execution_trace.append(
        {
            "step": "Tool executed",
            "details": evidence_result["summary"],
        }
    )

    analysis_results = []

    for tool_name in plan["analysis_tools"]:
        tool_function = ANALYSIS_TOOL_MAP.get(tool_name)

        if tool_function is None:
            continue

        analysis_result = tool_function(evidence_items)
        analysis_results.append(analysis_result)

        execution_trace.append(
            {
                "step": "Analysis tool executed",
                "details": f"{tool_name}: {analysis_result['summary']}",
            }
        )

    recommendation_result = generate_recommendation_tool(goal, evidence_items)
    answer = recommendation_result["answer"]

    execution_trace.append(
        {
            "step": "Recommendation generated",
            "details": "Generated CEO-level recommendation from retrieved evidence.",
        }
    )

    validation = validate_recommendation(answer, evidence_items)

    execution_trace.append(
        {
            "step": "Validation completed",
            "details": f"Validation passed: {validation['passed']}",
        }
    )

    memory_record = {
        "goal": goal,
        "goal_type": plan["goal_type"],
        "tools_used": plan["tools"],
        "evidence_count": len(evidence_items),
        "validation_passed": validation["passed"],
        "answer_preview": answer[:500],
    }

    memory_path = save_agent_run(memory_record)

    execution_trace.append(
        {
            "step": "Memory updated",
            "details": f"Agent run saved to {memory_path}",
        }
    )

    return {
        "answer": answer,
        "evidence_items": evidence_items,
        "valid_evidence_ids": recommendation_result.get("valid_evidence_ids", ""),
        "agent_goal": goal,
        "agent_plan": plan,
        "tools_used": plan["tools"],
        "analysis_results": analysis_results,
        "validation": validation,
        "recent_memory": recent_memory,
        "execution_trace": execution_trace,
    }


def test_agent():
    goal = input("Enter CEO goal: ").strip()

    result = run_ceo_agent(goal)

    print("\nAgent Plan")
    for step in result["agent_plan"].get("steps", []):
        print(f"- {step}")

    print("\nTools Used")
    for tool in result.get("tools_used", []):
        print(f"- {tool}")

    print("\nExecution Trace")
    for item in result.get("execution_trace", []):
        print(f"- {item['step']}: {item['details']}")

    print("\nValidation")
    print(result.get("validation", {}))

    print("\nFinal Answer")
    print(result.get("answer", ""))


if __name__ == "__main__":
    test_agent()