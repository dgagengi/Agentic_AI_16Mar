from langchain.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from app.tools.expense_tools import add_expense, get_expenses, set_budget, get_budgets, calculate_budget_summary
from typing import TypedDict, Optional, List
import os
from dotenv import load_dotenv

load_dotenv()

class FinancialState(TypedDict):
    query: str
    user_id: str
    response: Optional[str]
    need_human_input: bool
    human_input: Optional[str]
    messages: List

# LLMs
fast_llm = ChatGroq(model="llama-3.1-8b-instant", api_key=os.getenv("GROQ_API_KEY")).bind_tools([add_expense, get_expenses, set_budget, get_budgets, calculate_budget_summary])
detailed_llm = ChatGroq(model="llama-3.1-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))

def process_query(state: FinancialState) -> FinancialState:
    messages = [HumanMessage(content=state["query"])]
    ai_msg = fast_llm.invoke(messages)
    messages.append(ai_msg)
    if ai_msg.tool_calls:
        for tool_call in ai_msg.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_args["user_id"] = state["user_id"]  # Add user_id
            if tool_name == "add_expense":
                result = add_expense.invoke(tool_args)
            elif tool_name == "get_expenses":
                result = get_expenses.invoke({"user_id": state["user_id"]})
            elif tool_name == "set_budget":
                result = set_budget.invoke(tool_args)
            elif tool_name == "get_budgets":
                result = get_budgets.invoke({"user_id": state["user_id"]})
            elif tool_name == "calculate_budget_summary":
                result = calculate_budget_summary.invoke({"user_id": state["user_id"]})
            else:
                result = "Unknown tool"
            messages.append(ToolMessage(content=str(result), tool_call_id=tool_call["id"]))
        # Get final response
        final_msg = fast_llm.invoke(messages)
        state["response"] = final_msg.content
    else:
        state["response"] = ai_msg.content
    # Simple HITL check
    if "approve" in state["query"].lower():
        state["need_human_input"] = True
    else:
        state["need_human_input"] = False
    return state

def human_loop(state: FinancialState) -> FinancialState:
    if state["need_human_input"]:
        # Placeholder for human input
        state["human_input"] = "approved"
        state["response"] += f" Human approved."
    return state

def generate_tips(state: FinancialState) -> FinancialState:
    if "tip" in state["query"].lower() or "advice" in state["query"].lower():
        tip_prompt = f"Provide financial tips based on the following: {state['response']}"
        tip = detailed_llm.invoke(tip_prompt).content
        state["response"] += f" Financial Tip: {tip}"
    return state

# Graph
graph = StateGraph(FinancialState)
graph.add_node("process", process_query)
graph.add_node("human", human_loop)
graph.add_node("tips", generate_tips)

graph.set_entry_point("process")
graph.add_edge("process", "human")
graph.add_conditional_edges("human", lambda x: "tips" if not x["need_human_input"] else END)
graph.add_edge("tips", END)

financial_assistant_graph = graph.compile()