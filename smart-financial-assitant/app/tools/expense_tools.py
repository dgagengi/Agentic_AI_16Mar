from langchain.tools import tool
from typing import List, Dict
import json
from app.data import expenses_db, budgets_db

@tool
def add_expense(amount: float, category: str, description: str, user_id: str) -> str:
    """Add an expense for the user."""
    if user_id not in expenses_db:
        expenses_db[user_id] = []
    expenses_db[user_id].append({"amount": amount, "category": category, "description": description})
    return "Expense added successfully"

@tool
def get_expenses(user_id: str) -> str:
    """Get all expenses for the user."""
    expenses = expenses_db.get(user_id, [])
    return json.dumps(expenses)

@tool
def set_budget(category: str, limit: float, user_id: str) -> str:
    """Set budget limit for a category."""
    if user_id not in budgets_db:
        budgets_db[user_id] = {}
    budgets_db[user_id][category] = limit
    return "Budget set successfully"

@tool
def get_budgets(user_id: str) -> str:
    """Get all budgets for the user."""
    budgets = budgets_db.get(user_id, {})
    return json.dumps(budgets)

@tool
def calculate_budget_summary(user_id: str) -> str:
    """Calculate budget summary: total spent vs limits."""
    expenses = expenses_db.get(user_id, [])
    budgets = budgets_db.get(user_id, {})
    summary = {}
    total_spent = {}
    for exp in expenses:
        cat = exp["category"]
        total_spent[cat] = total_spent.get(cat, 0) + exp["amount"]
    for cat, limit in budgets.items():
        spent = total_spent.get(cat, 0)
        summary[cat] = {"limit": limit, "spent": spent, "remaining": limit - spent}
    return json.dumps(summary)