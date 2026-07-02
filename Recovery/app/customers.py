import streamlit as st

from services.analytics import prepare_recovery_data


def render_page() -> None:
    st.title("👥 Customer Analysis")

    if "df" not in st.session_state:
        st.warning("No data loaded.")
        return

    df = prepare_recovery_data(st.session_state["df"])

    statuses = sorted([s for s in df["Status"].dropna().unique()])
    selected_status = st.multiselect("Filter Status", statuses)
    customer_search = st.text_input("Search Customer")

    if selected_status:
        df = df[df["Status"].isin(selected_status)]

    if customer_search:
        df = df[df["Customer"].str.contains(customer_search, case=False, na=False)]

    st.subheader("Customer Records")
    display_columns = [
        col for col in ["Customer", "Status", "Balance", "Pay off amount", "Left to pay", "Amount paid", "Assigned to contractor", "Date"]
        if col in df.columns
    ]
    st.dataframe(df[display_columns], use_container_width=True)

    st.subheader("Customer Status Summary")
    summary = (
        df.groupby("Status")
        .agg(
            Customers=("Customer", "count"),
            Amount_Paid=("Amount paid", "sum"),
            Left_To_Pay=("Left to pay", "sum"),
        )
        .reset_index()
        .sort_values(["Customers", "Amount_Paid"], ascending=False)
    )
    st.dataframe(summary)
    st.bar_chart(summary.set_index("Status")["Customers"])


if __name__ == "__main__":
    render_page()