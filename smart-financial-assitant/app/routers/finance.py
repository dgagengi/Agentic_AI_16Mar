from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.graphs.financial_graph import financial_assistant_graph

router = APIRouter()

class Expense(BaseModel):
    amount: float
    category: str
    description: str

class Budget(BaseModel):
    category: str
    limit: float

class UserQuery(BaseModel):
    query: str
    user_id: str

# In-memory storage for demo
expenses_db = {}
budgets_db = {}

@router.post("/expenses")
async def add_expense(expense: Expense, user_id: str):
    if user_id not in expenses_db:
        expenses_db[user_id] = []
    expenses_db[user_id].append(expense.dict())
    return {"message": "Expense added"}

@router.get("/expenses/{user_id}")
async def get_expenses(user_id: str):
    return expenses_db.get(user_id, [])

@router.post("/budgets")
async def set_budget(budget: Budget, user_id: str):
    if user_id not in budgets_db:
        budgets_db[user_id] = {}
    budgets_db[user_id][budget.category] = budget.limit
    return {"message": "Budget set"}

@router.get("/budgets/{user_id}")
async def get_budgets(user_id: str):
    return budgets_db.get(user_id, {})

@router.post("/assist")
async def assist(user_query: UserQuery):
    try:
        result = financial_assistant_graph.invoke({"query": user_query.query, "user_id": user_query.user_id})
        return {"response": result["response"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))