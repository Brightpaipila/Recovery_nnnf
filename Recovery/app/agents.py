import pandas as pd
import plotly.express as px
import streamlit as st

from services.analytics import build_agent_summary, prepare_recovery_data


CHART_TEMPLATE = "plotly_white"


def _style_chart(fig):
    fig.update_layout(
        template=CHART_TEMPLATE,
        margin=dict(l=12, r=12, t=48, b=12),
        height=390,
        font=dict(family="Arial, sans-serif", size=13, color="#334155"),
        title_font=dict(size=18, color="#0F172A"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend_title_text="",
        hoverlabel=dict(bgcolor="white", font_size=12),
    )
    fig.update_xaxes(showgrid=False, title_text="")
    fig.update_yaxes(showgrid=True, gridcolor="#E2E8F0")
    return fig


def _build_agent_insights(df: pd.DataFrame, agent_summary: pd.DataFrame) -> pd.DataFrame:
    risk = (
        df.groupby("Assigned to contractor")
        .agg(
            Outstanding_Exposure=("Left to pay", "sum"),
            High_Risk_Accounts=("risk_level", lambda s: int((s == "High Risk").sum())),
            Problem_Cases=("problem_case", "sum"),
            Active_Accounts=("recovery_segment", lambda s: int(s.isin(["Active Payer", "Near Completion"]).sum())),
        )
        .reset_index()
    )

    insights = agent_summary.merge(risk, on="Assigned to contractor", how="left")
    insights["Outstanding_Exposure"] = insights["Outstanding_Exposure"].fillna(0)
    insights["High_Risk_Accounts"] = insights["High_Risk_Accounts"].fillna(0).astype(int)
    insights["Problem_Cases"] = insights["Problem_Cases"].fillna(0).astype(int)
    insights["Active_Accounts"] = insights["Active_Accounts"].fillna(0).astype(int)
    insights["Collection_per_Account"] = insights["Todays_Collections"] / insights["Customers"].replace(0, pd.NA)
    insights["Collection_per_Account"] = insights["Collection_per_Account"].fillna(0)
    insights["Risk_Load"] = insights["High_Risk_Accounts"] / insights["Customers"].replace(0, pd.NA)
    insights["Risk_Load"] = insights["Risk_Load"].fillna(0)
    insights["Exposure_per_Account"] = insights["Outstanding_Exposure"] / insights["Customers"].replace(0, pd.NA)
    insights["Exposure_per_Account"] = insights["Exposure_per_Account"].fillna(0)
    return insights.sort_values(["Todays_Collections", "Active_Accounts"], ascending=False)


def render_page() -> None:
    st.title("Agent Performance Intelligence")
    st.caption("Contractor collection performance, outstanding exposure, and operational risk")

    if "df" not in st.session_state:
        st.warning("No data loaded.")
        return

    df = prepare_recovery_data(st.session_state["df"])
    agent_summary = build_agent_summary(df)
    agent_insights = _build_agent_insights(df, agent_summary)

    st.subheader("Top Performing Agents")
    st.dataframe(
        agent_insights,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Todays_Collections": st.column_config.NumberColumn("Today's Collections", format="MWK %.0f"),
            "Cumulative_Paid": st.column_config.NumberColumn("Cumulative Paid", format="MWK %.0f"),
            "Outstanding_Exposure": st.column_config.NumberColumn("Outstanding Exposure", format="MWK %.0f"),
            "Collection_per_Account": None,
            "Problem_Cases": None,
            "Exposure_per_Account": st.column_config.NumberColumn("Average Amount Still Owed", format="MWK %.0f"),
            "Risk_Load": st.column_config.ProgressColumn("Risk Load", format="%.1f", min_value=0, max_value=1),
        },
    )

    col1, col2 = st.columns(2)

    with col1:
        collection_fig = px.bar(
            agent_insights.head(12),
            x="Assigned to contractor",
            y="Todays_Collections",
            color="Active_Accounts",
            color_continuous_scale=["#DBEAFE", "#2563EB"],
            text="Todays_Collections",
            title="Collections by Contractor",
            labels={
                "Assigned to contractor": "Contractor",
                "Todays_Collections": "Collected Today",
                "Active_Accounts": "Active Accounts",
            },
        )
        collection_fig.update_traces(texttemplate="MWK %{text:,.0f}", textposition="outside")
        collection_fig.update_yaxes(tickprefix="MWK ", separatethousands=True)
        st.plotly_chart(_style_chart(collection_fig), use_container_width=True)

    with col2:
        exposure_fig = px.scatter(
            agent_insights,
            x="Outstanding_Exposure",
            y="Todays_Collections",
            size="Customers",
            color="Risk_Load",
            color_continuous_scale=["#0F766E", "#F59E0B", "#DC2626"],
            hover_name="Assigned to contractor",
            hover_data={
                "Customers": ":,",
                "High_Risk_Accounts": ":,",
                "Active_Accounts": ":,",
                "Outstanding_Exposure": ":,.0f",
                "Todays_Collections": ":,.0f",
                "Risk_Load": ":.1%",
            },
            title="Contractor Exposure vs Collections",
            labels={
                "Outstanding_Exposure": "Outstanding Exposure",
                "Todays_Collections": "Collected Today",
                "Risk_Load": "Risk Load",
            },
        )
        exposure_fig.update_xaxes(tickprefix="MWK ", separatethousands=True)
        exposure_fig.update_yaxes(tickprefix="MWK ", separatethousands=True)
        st.plotly_chart(_style_chart(exposure_fig), use_container_width=True)

    st.subheader("Analytical Agent Insight")
    insight_table = agent_insights[
        [
            "Assigned to contractor",
            "Customers",
            "Active_Accounts",
            "High_Risk_Accounts",
            "Todays_Collections",
            "Outstanding_Exposure",
            "Exposure_per_Account",
            "Risk_Load",
        ]
    ].copy()
    insight_table["Operational_Reading"] = insight_table.apply(
        lambda row: "Strong collections, monitor exposure"
        if row["Todays_Collections"] > 0 and row["Risk_Load"] < 0.35
        else "High exposure, prioritize field follow-up"
        if row["Risk_Load"] >= 0.35
        else "Low daily movement, review account actions",
        axis=1,
    )
    st.dataframe(
        insight_table,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Todays_Collections": st.column_config.NumberColumn("Today's Collections", format="MWK %.0f"),
            "Outstanding_Exposure": st.column_config.NumberColumn("Outstanding Exposure", format="MWK %.0f"),
            "Exposure_per_Account": st.column_config.NumberColumn("Average Amount Still Owed", format="MWK %.0f"),
            "Risk_Load": st.column_config.ProgressColumn("Risk Load", format="%.1f", min_value=0, max_value=1),
        },
    )


if __name__ == "__main__":
    render_page()
