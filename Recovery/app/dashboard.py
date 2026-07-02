import pandas as pd
import streamlit as st

from services.analytics import build_agent_summary, build_kpi_summary, prepare_recovery_data


def _format_mwk(value: float) -> str:
    return f"MWK {value:,.0f}"


def render_page() -> None:
    st.title("RECOVERIES NNNF")
    st.caption("Recovery dashboard for customer payment tracking and contractor performance")

    if "df" not in st.session_state:
        st.warning("No data loaded.")
        return

    df = prepare_recovery_data(st.session_state["df"])

    if "Date" in df.columns:
        df["Date"] = df["Date"].astype(str)
        available_dates = sorted(df["Date"].dropna().unique().tolist())
        selected_dates = st.multiselect("Filter by Date", available_dates, default=available_dates)
        if selected_dates:
            df = df[df["Date"].isin(selected_dates)]

    summary = build_kpi_summary(df)

    st.subheader("Recovery KPIs")
    metrics = st.columns(4)
    metrics[0].metric("Total Customers", f"{summary['customers']:,}")
    metrics[1].metric("Amount Paid Today", _format_mwk(summary['today_amount_paid']))
    metrics[2].metric("Balance Paid So Far", _format_mwk(summary['balance_paid']))
    metrics[3].metric("Left to Pay", _format_mwk(summary['outstanding']))

    st.divider()

    status_summary = (
        df.groupby("Status")
        .agg(
            Customers=("Customer", "count"),
            Amount_Paid=("Amount paid", "sum"),
            Left_To_Pay=("Left to pay", "sum"),
        )
        .reset_index()
        .sort_values(["Customers", "Amount_Paid"], ascending=False)
    )

    st.subheader("Status KPI Summary")
    st.dataframe(status_summary, use_container_width=True)

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("STATUS DISTRIBUTION")
        st.bar_chart(status_summary.set_index("Status")["Customers"])

    with col2:
        st.subheader("AGENT PERFORMANCE")
        agent_summary = build_agent_summary(df)
        if not agent_summary.empty:
            st.bar_chart(agent_summary.set_index("Assigned to contractor")["Todays_Collections"])
        else:
            st.info("No agent data available")

    st.divider()

    st.subheader("DAILY COLLECTION TREND")
    if "Date" in df.columns:
        trend = (
            df.groupby("Date")
            .agg(Today_Paid=("Amount paid", "sum"))
            .reset_index()
        )
        st.line_chart(trend.set_index("Date"))
    else:
        st.info("No date column available for trend chart")

    st.divider()
    st.subheader("Latest Customer Recovery Records")
    display_columns = [
        col for col in ["Customer", "Status", "Balance", "Pay off amount", "Left to pay", "Amount paid", "Assigned to contractor", "Date"]
        if col in df.columns
    ]
    st.dataframe(df[display_columns], use_container_width=True)


if __name__ == "__main__":
    render_page()