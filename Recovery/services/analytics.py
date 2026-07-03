from __future__ import annotations

import pandas as pd


def _parse_currency(value) -> float:
    if pd.isna(value):
        return 0.0

    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip()
    if not text:
        return 0.0

    text = text.replace("MK", "", 1).replace(",", "").replace(" ", "")
    try:
        return float(text)
    except ValueError:
        return 0.0


def _find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    normalized = {col.strip().lower(): col for col in df.columns}

    for candidate in candidates:
        key = candidate.strip().lower()
        if key in normalized:
            return normalized[key]

    for col in df.columns:
        lowered = col.strip().lower()
        if any(candidate.lower() in lowered for candidate in candidates):
            return col

    return None


def normalize_recovery_columns(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    column_map = {}

    balance_col = _find_column(cleaned, ["Balance", "balance", "Amount paid so far", "amount paid so far"])
    pay_off_col = _find_column(cleaned, ["Pay off amount", "pay off amount", "Payoff amount", "payoff amount", "Total cost", "total cost"])
    left_to_pay_col = _find_column(cleaned, ["Left to pay", "left to pay", "Remaining balance", "remaining balance"])
    amount_paid_col = _find_column(cleaned, ["Amount paid", "amount paid", "Today payment", "today payment", "Daily payment", "daily payment"])
    status_col = _find_column(cleaned, ["Status", "status"])
    customer_col = _find_column(cleaned, ["Customer", "customer", "Customer name", "customer name"])
    agent_col = _find_column(cleaned, ["Assigned to contractor", "assigned to contractor", "Agent", "agent", "Contractor", "contractor"])

    if balance_col and balance_col != "Balance":
        column_map[balance_col] = "Balance"
    if pay_off_col and pay_off_col != "Pay off amount":
        column_map[pay_off_col] = "Pay off amount"
    if left_to_pay_col and left_to_pay_col != "Left to pay":
        column_map[left_to_pay_col] = "Left to pay"
    if amount_paid_col and amount_paid_col != "Amount paid":
        column_map[amount_paid_col] = "Amount paid"
    if status_col and status_col != "Status":
        column_map[status_col] = "Status"
    if customer_col and customer_col != "Customer":
        column_map[customer_col] = "Customer"
    if agent_col and agent_col != "Assigned to contractor":
        column_map[agent_col] = "Assigned to contractor"

    cleaned = cleaned.rename(columns=column_map)

    for col in ["Balance", "Pay off amount", "Left to pay", "Amount paid"]:
        if col in cleaned.columns:
            cleaned[col] = cleaned[col].apply(_parse_currency)

    if "Status" not in cleaned.columns:
        cleaned["Status"] = "Unknown"
    else:
        cleaned["Status"] = cleaned["Status"].fillna("Unknown").astype(str)

    if "Customer" not in cleaned.columns:
        cleaned["Customer"] = [f"Customer {idx + 1}" for idx in range(len(cleaned))]

    if "Assigned to contractor" not in cleaned.columns:
        cleaned["Assigned to contractor"] = "Unassigned"

    return cleaned


def prepare_recovery_data(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = normalize_recovery_columns(df).copy()
    cleaned["problem_case"] = (
        cleaned["Status"].str.contains("fault|stolen|relocat|unavail|problem|not reachable|wrong number", case=False, na=False)
    )

    balance = cleaned["Balance"]
    pay_off = cleaned["Pay off amount"]
    left_to_pay = cleaned["Left to pay"]
    amount_paid = cleaned["Amount paid"]

    paid_status = cleaned["Status"].str.strip().str.lower() == "paid"

    completed = left_to_pay <= 0

    cleaned["recovery_segment"] = "Needs Follow-up"
    cleaned.loc[(amount_paid > 0) & (left_to_pay > 0) & (left_to_pay <= (pay_off * 0.2)), "recovery_segment"] = "Near Completion"
    cleaned.loc[(amount_paid > 0) & (left_to_pay > 0) & (left_to_pay > (pay_off * 0.5)), "recovery_segment"] = "Active Payer"
    cleaned.loc[paid_status & (~completed), "recovery_segment"] = "Paid"
    cleaned.loc[completed, "recovery_segment"] = "Completed"

    cleaned["risk_level"] = "Medium Risk"
    cleaned.loc[(cleaned["recovery_segment"].isin(["Paid", "Completed"])), "risk_level"] = "Low Risk"
    cleaned.loc[(cleaned["problem_case"]) & (amount_paid == 0), "risk_level"] = "High Risk"
    cleaned.loc[(cleaned["recovery_segment"] == "Near Completion"), "risk_level"] = "Low Risk"

    return cleaned


def build_kpi_summary(df: pd.DataFrame) -> dict[str, float | int]:
    cleaned = prepare_recovery_data(df)
    if cleaned.empty:
        return {
            "customers": 0,
            "today_amount_paid": 0.0,
            "balance_paid": 0.0,
            "outstanding": 0.0,
        }

    total_payoff = cleaned["Pay off amount"].sum()
    total_balance = cleaned["Balance"].sum()
    outstanding = cleaned["Left to pay"].sum()
    total_today_paid = cleaned["Amount paid"].sum()
    balance_paid_so_far = total_balance + outstanding
    return {
        "customers": int(len(cleaned)),
        "today_amount_paid": round(float(total_today_paid), 2),
        "balance_paid": round(float(balance_paid_so_far), 2),
        "outstanding": round(float(outstanding), 2),
    }


def build_agent_summary(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = prepare_recovery_data(df)
    summary = (
        cleaned.groupby("Assigned to contractor")
        .agg(
            Customers=("Customer", "count"),
            Todays_Collections=("Amount paid", "sum"),
            Cumulative_Paid=("Balance", "sum"),
            Paid_Customers=("Status", lambda s: int(((s.astype(str).str.lower() == "paid") | (cleaned.loc[s.index, "Left to pay"] <= 0)).sum())),
            
        )
        .reset_index()
    )
    summary = summary.sort_values("Todays_Collections", ascending=False)
    return summary





def summarize_metrics(df: pd.DataFrame) -> dict[str, float]:
    if df.empty:
        return {"customers": 0, "open_balance": 0.0, "weekly_collection": 0.0}

    return {
        "customers": int(len(df)),
        "open_balance": round(float(df["balance"].sum()), 2),
        "weekly_collection": round(float(df["weekly_payment"].sum()), 2),
    }
