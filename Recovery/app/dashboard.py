import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from services.analytics import build_agent_summary, build_kpi_summary, prepare_recovery_data


CHART_TEMPLATE = "plotly_white"
SEGMENT_COLORS = {
    "Paid": "#0F766E",
    "Completed": "#14B8A6",
    "Near Completion": "#22C55E",
    "Active Payer": "#2563EB",
    "Needs Follow-up": "#F59E0B",
}


def _format_mwk(value: float) -> str:
    return f"MWK {value:,.0f}"


def _style_chart(fig: go.Figure, yaxis_title: str | None = None) -> go.Figure:
    fig.update_layout(
        template=CHART_TEMPLATE,
        margin=dict(l=12, r=12, t=48, b=12),
        height=380,
        font=dict(family="Arial, sans-serif", size=13, color="#334155"),
        title_font=dict(size=18, color="#0F172A"),
        legend_title_text="",
        hoverlabel=dict(bgcolor="white", font_size=12),
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    fig.update_xaxes(showgrid=False, title_text="")
    fig.update_yaxes(showgrid=True, gridcolor="#E2E8F0", title_text=yaxis_title)
    return fig


def _currency_axis(fig: go.Figure) -> go.Figure:
    fig.update_yaxes(tickprefix="MWK ", separatethousands=True)
    return fig


def _recovery_kpi_table(summary: dict[str, float | int], df: pd.DataFrame) -> pd.DataFrame:
    total_due = float(df["Pay off amount"].sum()) if "Pay off amount" in df.columns else 0.0
    collected_total = float(df["Balance"].sum()) if "Balance" in df.columns else 0.0
    outstanding = float(summary["outstanding"])
    active_customers = int((df["recovery_segment"].isin(["Active Payer", "Near Completion"])).sum())
    

    return pd.DataFrame(
        [
            {"KPI": "Total Contract Value", "Value": _format_mwk(total_due), "Meaning": "Full recoverable portfolio value"},
            {"KPI": "Collected to Date", "Value": _format_mwk(collected_total), "Meaning": "Cumulative cash already recovered"},
            {"KPI": "Outstanding Exposure", "Value": _format_mwk(outstanding), "Meaning": "Cash still pending collection"},
            {"KPI": "Active Customers Today", "Value": f"{active_customers:,}", "Meaning": "Customers who paid Today"},
            
        ]
    )


def render_page() -> None:
    st.title("NNNF Recovery Dashboard")
    st.caption("International-standard portfolio view for collections, outstanding exposure, and contractor performance")

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

    st.dataframe(_recovery_kpi_table(summary, df), use_container_width=True, hide_index=True)

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
    status_summary["Collection_Rate"] = status_summary["Amount_Paid"] / (
        status_summary["Amount_Paid"] + status_summary["Left_To_Pay"]
    ).replace(0, pd.NA)
    status_summary["Collection_Rate"] = status_summary["Collection_Rate"].fillna(0)

    segment_summary = (
        df.groupby("recovery_segment")
        .agg(
            Customers=("Customer", "count"),
            Amount_Paid=("Amount paid", "sum"),
            Left_To_Pay=("Left to pay", "sum"),
        )
        .reset_index()
        .sort_values("Customers", ascending=False)
    )
    segment_summary = segment_summary[
        ~segment_summary["recovery_segment"].isin(["Defaulter", "Problem Case"])
    ]

    st.subheader("Status KPI Summary")
    st.dataframe(
        status_summary,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Amount_Paid": st.column_config.NumberColumn("Amount Paid", format="MWK %.0f"),
            "Left_To_Pay": st.column_config.NumberColumn("Left to Pay", format="MWK %.0f"),
            "Collection_Rate": st.column_config.ProgressColumn("Collection Rate", format="%.1f", min_value=0, max_value=1),
        },
    )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            segment_summary,
            x="recovery_segment",
            y="Customers",
            color="recovery_segment",
            color_discrete_map=SEGMENT_COLORS,
            text="Customers",
            title="Recovery Portfolio Segmentation",
            labels={"recovery_segment": "Segment", "Customers": "Customers"},
        )
        fig.update_traces(textposition="outside", hovertemplate="<b>%{x}</b><br>Customers: %{y:,}<extra></extra>")
        st.plotly_chart(_style_chart(fig, "Customers"), use_container_width=True)

    with col2:
        agent_summary = build_agent_summary(df)
        if not agent_summary.empty:
            agent_fig = px.bar(
                agent_summary.head(10),
                x="Assigned to contractor",
                y="Todays_Collections",
                color="Customers",
                color_continuous_scale=["#DBEAFE", "#2563EB"],
                text="Todays_Collections",
                title="Contractor Collections",
                labels={"Assigned to contractor": "Contractor", "Todays_Collections": "Collected Today", "Customers": "Accounts"},
            )
            agent_fig.update_traces(texttemplate="MWK %{text:,.0f}", textposition="outside")
            agent_fig.update_layout(coloraxis_colorbar_title="Accounts")
            st.plotly_chart(_currency_axis(_style_chart(agent_fig, "Collected Today")), use_container_width=True)
        else:
            st.info("No agent data available")

    st.divider()

    if "Date" in df.columns:
        trend = (
            df.groupby("Date")
            .agg(Today_Paid=("Amount paid", "sum"), Customers=("Customer", "count"))
            .reset_index()
        )
        trend_fig = px.line(
            trend,
            x="Date",
            y="Today_Paid",
            markers=True,
            title="Daily Collections Trend",
            labels={"Today_Paid": "Collected", "Date": "Date"},
            hover_data={"Customers": ":,"},
        )
        trend_fig.update_traces(line=dict(color="#0F766E", width=3), hovertemplate="<b>%{x}</b><br>Collected: MWK %{y:,.0f}<extra></extra>")
        st.plotly_chart(_currency_axis(_style_chart(trend_fig, "Collected")), use_container_width=True)
    else:
        st.info("No date column available for trend chart")

    exposure_fig = px.treemap(
        segment_summary,
        path=["recovery_segment"],
        values="Left_To_Pay",
        color="Amount_Paid",
        color_continuous_scale=["#FEE2E2", "#F59E0B", "#0F766E"],
        title="Recovery Segment",
        labels={"Left_To_Pay": "Outstanding", "Amount_Paid": "Collected"},
    )
    exposure_fig.update_traces(
        texttemplate="<b>%{label}</b><br>MWK %{value:,.0f}",
        hovertemplate="<b>%{label}</b><br>Outstanding: MWK %{value:,.0f}<extra></extra>",
    )
    st.plotly_chart(_style_chart(exposure_fig), use_container_width=True)

    st.divider()
    st.subheader("Customer Recovery Records")
    display_columns = [
        col for col in ["Customer", "Status", "Balance", "Pay off amount", "Left to pay", "Amount paid", "Assigned to contractor", "Date"]
        if col in df.columns
    ]
    st.dataframe(
        df[display_columns],
        use_container_width=True,
        column_config={
            "Balance": st.column_config.NumberColumn("Balance", format="MWK %.0f"),
            "Pay off amount": st.column_config.NumberColumn("Pay off amount", format="MWK %.0f"),
            "Left to pay": st.column_config.NumberColumn("Left to pay", format="MWK %.0f"),
            "Amount paid": st.column_config.NumberColumn("Amount paid", format="MWK %.0f"),
        },
    )


if __name__ == "__main__":
    render_page()
