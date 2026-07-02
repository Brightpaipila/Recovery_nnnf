import importlib
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from config.settings import SHEETS
from services.analytics import _parse_currency
from services.google_sheets import list_worksheets, load_multiple_worksheets


def render_page() -> None:
    st.set_page_config(page_title="NNNF Recovery System", layout="wide")

    logo_path = Path(__file__).resolve().parent / "Recapo Logo.png"
    if logo_path.exists():
        try:
            from PIL import Image

            st.image(Image.open(logo_path), width=100)
        except Exception:
            st.caption("Recovery Dashboard")

    st.title("RECAPO SOLAR SYSTEMS")

    sheet_name = st.sidebar.selectbox("Select Recovery Sheet", list(SHEETS.keys()))
    sheet_url = SHEETS[sheet_name]

    try:
        worksheets = list_worksheets(sheet_url)
    except Exception as e:
        st.error(f"Error loading sheets: {e}")
        st.stop()

    selected_tabs = st.sidebar.multiselect("Select Daily Sheets", worksheets, default=worksheets)

    if not selected_tabs:
        st.warning("Select at least one sheet to load data")
        return

    df = load_multiple_worksheets(sheet_url, selected_tabs)
    for col in ["Amount paid", "Left to pay", "Balance", "Pay off amount"]:
        if col in df.columns:
            df[col] = df[col].apply(_parse_currency)

    st.session_state["df"] = df
    st.success(f"Loaded {len(df)} records")

    page = st.sidebar.radio("Navigate", ["Dashboard", "Agents", "Customers"])
    page_modules = {
        "Dashboard": "app.dashboard",
        "Agents": "app.agents",
        "Customers": "app.customers",
    }

    module = importlib.import_module(page_modules[page])
    if hasattr(module, "render_page"):
        module.render_page()
    else:
        st.error("This page has not been implemented yet.")


if __name__ == "__main__":
    render_page()