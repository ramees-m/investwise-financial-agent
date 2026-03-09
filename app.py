# app.py

import streamlit as st
from agents import run_financial_analysis

# ---------------------------
# Page Config
# ---------------------------

st.set_page_config(
    page_title="InvestWise",
    page_icon="💹",
    layout="wide"
)

# ---------------------------
# Session State (Page Control)
# ---------------------------

if "page" not in st.session_state:
    st.session_state.page = "input"

if "result" not in st.session_state:
    st.session_state.result = None


# ---------------------------
# PAGE 1 : INPUT PAGE
# ---------------------------

if st.session_state.page == "input":

    st.markdown(
        """
        <div style='text-align:center'>
            <h1>💹 InvestWiseAI</h1>
            <p style='font-size:18px;color:gray'>
            AI-Powered Financial Analysis & Investment Insights
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    col1, col2, col3 = st.columns([1,2,1])

    with col2:

        st.subheader("🔍 Analyze a Company")

        company = st.text_input(
            "Company Ticker",
            placeholder="Example: AAPL, TSLA, MSFT"
        )
        st.write("")

        query = st.text_area(
            "Investment Question",
            placeholder="Example: Should I invest in this company for long-term growth?"


        )
        st.markdown("<br>", unsafe_allow_html=True)

        analyze = st.button("➜] Analysis")

        if analyze:

            if company and query:

                with st.spinner("Running multi-agent financial analysis..."):

                    result = run_financial_analysis(company, query)

                    st.session_state.result = result
                    st.session_state.page = "report"

                    st.rerun()

            else:
                st.warning("Please enter both company ticker and question.")


# ---------------------------
# PAGE 2 : REPORT PAGE
# ---------------------------

elif st.session_state.page == "report":

    result = st.session_state.result

    st.markdown(
        """
        <div style='text-align:center'>
            <h1>📊 InvestWise Financial Report</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.success("Analysis Complete")

    st.divider()

    # ---------------------------
    # Financial Data
    # ---------------------------

    st.subheader("📈 Financial Data")

    st.json(result.get("financial_data", {}))

    st.divider()

    # ---------------------------
    # Analysis Metrics
    # ---------------------------

    st.subheader("📊 Financial Analysis")

    st.json(result.get("analysis_results", {}))

    st.divider()

    # ---------------------------
    # Risk Level
    # ---------------------------

    st.subheader("⚠️ Risk Level")

    risk = result.get("risk_level", "Unknown")

    if risk == "Low":
        st.success(f"Risk Level: {risk}")
    elif risk == "Medium":
        st.warning(f"Risk Level: {risk}")
    else:
        st.error(f"Risk Level: {risk}")

    st.divider()

    # ---------------------------
    # Investment Advice
    # ---------------------------

    st.subheader("💡 Investment Advice")

    st.json(result.get("advice", {}))

    st.divider()

    # ---------------------------
    # Summary Note
    # ---------------------------

    st.subheader("📄 Summary")

    st.write(result.get("summary_note", "Summary not available"))

    st.divider()

    # ---------------------------
    # Back Button
    # ---------------------------

    if st.button(" ↩ "):

        st.session_state.page = "input"
        st.session_state.result = None

        st.rerun()