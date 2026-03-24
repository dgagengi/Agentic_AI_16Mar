import streamlit as st
from app.graphs.financial_graph import financial_assistant_graph
from app.data import expenses_db, budgets_db
import json

st.title("Smart Financial Assistant")

# Sidebar for user ID
user_id = st.sidebar.text_input("User ID", value="user1")

# Tabs for different features
tab1, tab2, tab3, tab4 = st.tabs(["Expenses", "Budgets", "Budget Summary", "AI Assistant"])

with tab1:
    st.header("Manage Expenses")
    amount = st.number_input("Amount", min_value=0.0)
    category = st.text_input("Category")
    description = st.text_input("Description")
    if st.button("Add Expense"):
        if amount > 0 and category and description:
            if user_id not in expenses_db:
                expenses_db[user_id] = []
            expenses_db[user_id].append({"amount": amount, "category": category, "description": description})
            st.success("Expense added!")
        else:
            st.error("Please fill all fields")

    st.subheader("Your Expenses")
    if user_id in expenses_db:
        st.json(expenses_db[user_id])
    else:
        st.write("No expenses yet.")

with tab2:
    st.header("Manage Budgets")
    budget_category = st.text_input("Budget Category")
    limit = st.number_input("Limit", min_value=0.0)
    if st.button("Set Budget"):
        if budget_category and limit > 0:
            if user_id not in budgets_db:
                budgets_db[user_id] = {}
            budgets_db[user_id][budget_category] = limit
            st.success("Budget set!")
        else:
            st.error("Please fill all fields")

    st.subheader("Your Budgets")
    if user_id in budgets_db:
        st.json(budgets_db[user_id])
    else:
        st.write("No budgets set.")

with tab3:
    st.header("Budget Summary")
    if st.button("Generate Summary"):
        try:
            from app.tools.expense_tools import calculate_budget_summary
            result = calculate_budget_summary.invoke({"user_id": user_id})
            st.write("Budget Summary:", result)
        except Exception as e:
            st.error(str(e))

with tab4:
    st.header("AI Financial Assistant")
    query = st.text_input("Ask me anything about your finances")
    if st.button("Ask"):
        if query:
            try:
                result = financial_assistant_graph.invoke({"query": query, "user_id": user_id, "messages": []})
                st.write("Response:", result["response"])
            except Exception as e:
                st.error(str(e))
        else:
            st.error("Please enter a query")

if __name__ == "__main__":
    st.write("Run with: streamlit run main.py")