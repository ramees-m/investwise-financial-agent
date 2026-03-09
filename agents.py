# agents.py

from unittest import result

from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
import yfinance as yf


# ---------------------------
# LLM
# ---------------------------

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    api_key="api_key_goes_here"
)


# ---------------------------
# Shared Memory
# ---------------------------

class FinancialState(TypedDict):

    user_query: str
    company: str
    metrics_needed: list
    financial_data: dict
    analysis_results: dict
    risk_level: str
    advice: str
    summary_note: str 

# ---------------------------
# Planner Agent
# ---------------------------

def planner_agent(state: FinancialState):

    print("\n--- Planner Agent ---")

    prompt = f"""
You are a financial planning agent.

Your task:
1. Read the user request.
2. Identify which financial metrics are required to analyze the investment.

User request:
{state['user_query']}

Return the required financial metrics.

Possible metrics include:
- revenue
- net_income
- total_debt
- total_assets
- stock_price
- eps
- market_cap
- operating_cashflow

Respond as a Python list.
"""

    response = llm.invoke(prompt)

    print("Planner reasoning:", response.content)

    metrics = [
        "revenue",
        "net_income",
        "total_debt",
        "total_assets",
        "stock_price",
        "eps"
    ]

    state["metrics_needed"] = metrics

    return state


# ---------------------------
# Data Agent
# ---------------------------

def data_agent(state: FinancialState):

    print("\n--- Data Agent ---")

    prompt = f"""
You are a financial data retrieval agent.

Your job is to collect financial metrics for a company.

Company: {state['company']}

Metrics required:
{state['metrics_needed']}

Explain briefly how financial APIs like Yahoo Finance can be used to fetch this data.
"""

    explanation = llm.invoke(prompt)

    print(explanation.content)

    ticker = yf.Ticker(state["company"])

    info = ticker.info

    data = {

        "revenue": info.get("totalRevenue"),
        "net_income": info.get("netIncomeToCommon"),
        "total_debt": info.get("totalDebt"),
        "total_assets": info.get("totalAssets"),
        "stock_price": info.get("currentPrice"),
        "eps": info.get("trailingEps")

    }

    state["financial_data"] = data

    print("Fetched data:", data)

    return state


# ---------------------------
# Analyzer Agent
# ---------------------------

def analyzer_agent(state: FinancialState):

    print("\n--- Analyzer Agent ---")

    data = state["financial_data"]

    revenue = data.get("revenue", 1)
    net_income = data.get("net_income", 0)
    debt = data.get("total_debt", 0)
    assets = data.get("total_assets", 1)
    price = data.get("stock_price", 1)
    eps = data.get("eps", 1)

    profit_margin = net_income / revenue if revenue else 0
    debt_ratio = debt / assets if assets else 0
    pe_ratio = price / eps if eps else 0

    prompt = f"""
You are a financial analysis agent.

Using the calculated metrics:

Profit Margin: {profit_margin}
Debt Ratio: {debt_ratio}
P/E Ratio: {pe_ratio}

Explain what these metrics indicate about the company's financial health.
"""

    explanation = llm.invoke(prompt)

    print(explanation.content)

    state["analysis_results"] = {
        "profit_margin": profit_margin,
        "debt_ratio": debt_ratio,
        "pe_ratio": pe_ratio
    }

    return state


# ---------------------------
# Risk Agent
# ---------------------------

def risk_agent(state: FinancialState):

    print("\n--- Risk Agent ---")

    results = state["analysis_results"]

    prompt = f"""
You are a financial risk evaluation agent.

Given these financial metrics:

Profit Margin: {results['profit_margin']}
Debt Ratio: {results['debt_ratio']}
P/E Ratio: {results['pe_ratio']}

Classify investment risk as:

Low
Medium
High

Explain your reasoning.
"""

    response = llm.invoke(prompt)

    print(response.content)

    debt_ratio = results["debt_ratio"]

    if debt_ratio > 0.6:
        risk = "High"
    elif debt_ratio > 0.3:
        risk = "Medium"
    else:
        risk = "Low"

    state["risk_level"] = risk

    return state


# ---------------------------
# Advisor Agent
# ---------------------------

def advisor_agent(state: FinancialState):

    print("\n--- Advisor Agent ---")

    prompt = f"""
You are an investment advisor agent.

User request:
{state['user_query']}

Financial analysis results:
{state['analysis_results']}

Risk level:
{state['risk_level']}

Provide an investment recommendation.

Return ONLY in this JSON format:

{{
"risk_summary": "short explanation of the risk",
"key_insight": "main financial insight",
"recommendation": "Buy or Hold or Avoid"
}}

Do not include any extra text outside the JSON.
"""

    response = llm.invoke(prompt)

    import json

    try:
        advice = json.loads(response.content)
    except:
        advice = {
            "risk_summary": "Not parsed",
            "key_insight": "Not parsed",
            "recommendation": "Unknown"
        }

    print("\nAdvisor Output:")
    print(advice)

    state["advice"] = advice

    return state


# ---------------------------
# Summary Agent
# ---------------------------

def summary_agent(state: FinancialState):
    print("\n--- Summary Agent ---")

    prompt = f"""
Write a professional, concise financial summary note for the user.

Financial Data: {state['financial_data']}
Analysis: {state['analysis_results']}
Risk Level: {state['risk_level']}
Investment Advice: {state['advice']}

Make it readable, structured, and clear for investors.
"""
    response = llm.invoke(prompt)
    summary_note = response.content
    state["summary_note"] = summary_note

    print("\n📄 Summary Note:")
    print(summary_note)
    return state

# ---------------------------
# Graph Flow
# ---------------------------

builder = StateGraph(FinancialState)

builder.add_node("planner", planner_agent)
builder.add_node("data", data_agent)
builder.add_node("analyzer", analyzer_agent)
builder.add_node("risk", risk_agent)
builder.add_node("advisor", advisor_agent)
builder.add_node("summary", summary_agent)

builder.set_entry_point("planner")

builder.add_edge("planner", "data")
builder.add_edge("data", "analyzer")
builder.add_edge("analyzer", "risk")
builder.add_edge("risk", "advisor")
builder.add_edge("advisor", "summary")
builder.add_edge("summary", END)

graph = builder.compile()


# ---------------------------
# Run Function
# ---------------------------

def run_financial_analysis(company, query):

    initial_state = {

        "user_query": query,
        "company": company,
        "metrics_needed": [],
        "financial_data": {},
        "analysis_results": {},
        "risk_level": "",
        "advice": "",
        "summary_note": "" 

    }

    result = graph.invoke(initial_state)

    return result