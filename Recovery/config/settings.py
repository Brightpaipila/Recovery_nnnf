from pathlib import Path
import os

# -------------------------
# BASE PATHS
# -------------------------
BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = BASE_DIR / "outputs"

# Ensure outputs folder exists
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------
# SECURE CREDENTIALS PATH
# -------------------------
# Default secure location (NOT in Git)
DEFAULT_CREDENTIALS_PATH = r"D:\Work\RECAPO\Code Base\Secure\service_account.json"

SERVICE_ACCOUNT_PATH = Path(
    os.getenv("SERVICE_ACCOUNT_PATH", DEFAULT_CREDENTIALS_PATH)
)

# -------------------------
# OUTPUT FILES
# -------------------------
MASTER_DATA_PATH = OUTPUTS_DIR / "MASTER_E_STOVE.xlsx"
CLEAN_DATA_PATH = OUTPUTS_DIR / "eStove_clean_data.xlsx"
KPI_REPORT_PATH = OUTPUTS_DIR / "eStove_kpi_report.xlsx"

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
    "July 2026 NNNF Follow Ups":
        "https://docs.google.com/spreadsheets/d/12kKSZIKCAvy2R06jz--VEowtHa70hUee6u5QMCALdQk/edit",

    "June 2026 NNNF Follow Ups":
        "https://docs.google.com/spreadsheets/d/1GqI8dNVsyZL0ObZm5DO2YPbfUron-0D8S25dQ_JZHF4/edit",
}