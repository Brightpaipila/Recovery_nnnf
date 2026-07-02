import streamlit as st

from services.analytics import build_agent_summary, prepare_recovery_data


def render_page() -> None:
    st.title("👷 Agent Performance")

    if "df" not in st.session_state:
        st.warning("No data loaded.")
        return

    df = prepare_recovery_data(st.session_state["df"])
    agent_summary = build_agent_summary(df)

    st.subheader("Top Performing Agents")
    st.dataframe(agent_summary, use_container_width=True)

    st.subheader("Collections by Agent")
    chart = agent_summary[["Assigned to contractor", "Todays_Collections"]].set_index("Assigned to contractor")
    st.bar_chart(chart)

    st.subheader("Conversion Rate by Agent")
    rate_chart = agent_summary[["Assigned to contractor", "Conversion_Rate"]].set_index("Assigned to contractor")
    st.bar_chart(rate_chart)

    st.subheader("Problem Case Ratio")
    problem_chart = agent_summary[["Assigned to contractor", "Problem_Ratio"]].set_index("Assigned to contractor")
    st.bar_chart(problem_chart)


if __name__ == "__main__":
    render_page()