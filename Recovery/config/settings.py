from pathlib import Path
import os
import streamlit as st

# -------------------------
# BASE PATHS
# -------------------------
BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = BASE_DIR / "outputs"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------
# GOOGLE CREDENTIALS (Local + Cloud)
# -------------------------
DEFAULT_CREDENTIALS_PATH = r"D:\Work\RECAPO\Code Base\Secure\service_account.json"

# For Streamlit Cloud
if "service_account" in st.secrets:
    SERVICE_ACCOUNT_INFO = dict(st.secrets["service_account"])
    SERVICE_ACCOUNT_PATH = None
else:
    # Local development fallback
    SERVICE_ACCOUNT_PATH = Path(
        os.getenv("SERVICE_ACCOUNT_PATH", DEFAULT_CREDENTIALS_PATH)
    )
    SERVICE_ACCOUNT_INFO = None

# -------------------------
# GOOGLE SCOPES
# -------------------------
GOOGLE_SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

# -------------------------
# GOOGLE SHEETS SOURCES
# -------------------------
SHEETS = {
    "July 2026 NNNF Follow Ups": "https://docs.google.com/spreadsheets/d/12kKSZIKCAvy2R06jz--VEowtHa70hUee6u5QMCALdQk/edit",
    "June 2026 NNNF Follow Ups": "https://docs.google.com/spreadsheets/d/1GqI8dNVsyZL0ObZm5DO2YPbfUron-0D8S25dQ_JZHF4/edit",
}