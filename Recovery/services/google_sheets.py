import pandas as pd

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:  # pragma: no cover - handled gracefully at runtime
    gspread = None
    Credentials = None

from config.settings import GOOGLE_SCOPES, SERVICE_ACCOUNT_PATH, SERVICE_ACCOUNT_INFO


def _normalize_headers(headers):
    cleaned = []
    seen = {}

    for index, header in enumerate(headers):
        name = str(header).strip() if header is not None else ""
        if not name:
            name = f"Column_{index + 1}"

        base_name = name
        count = seen.get(base_name, 0)
        if count:
            name = f"{base_name}_{count + 1}"
        seen[base_name] = count + 1
        cleaned.append(name)

    return cleaned


def _rows_to_dataframe(values):
    if not values:
        return pd.DataFrame()

    first_non_empty_idx = None
    for idx, row in enumerate(values):
        if any(str(cell).strip() for cell in row):
            first_non_empty_idx = idx
            break

    if first_non_empty_idx is None:
        return pd.DataFrame()

    header_row = values[first_non_empty_idx]
    headers = _normalize_headers(header_row)

    data_rows = []
    for row in values[first_non_empty_idx + 1:]:
        if not any(str(cell).strip() for cell in row):
            continue

        padded = list(row) + [""] * max(0, len(headers) - len(row))
        if len(padded) < len(headers):
            padded = padded[: len(headers)]
        data_rows.append(padded)

    if not data_rows:
        return pd.DataFrame(columns=headers)

    return pd.DataFrame(data_rows, columns=headers)


def get_client():
    if gspread is None or Credentials is None:
        raise ImportError(
            "gspread and google-auth are required to read Google Sheets. "
            "Install them with 'pip install gspread google-auth'."
        )

    try:
        if SERVICE_ACCOUNT_INFO is not None:
            # Streamlit Cloud - using st.secrets
            creds = Credentials.from_service_account_info(
                SERVICE_ACCOUNT_INFO, scopes=GOOGLE_SCOPES
            )
        else:
            # Local development - using JSON file
            creds = Credentials.from_service_account_file(
                SERVICE_ACCOUNT_PATH, scopes=GOOGLE_SCOPES
            )
        return gspread.authorize(creds)
    except Exception as e:
        raise Exception(f"Failed to authenticate with Google Sheets: {str(e)}")


def list_worksheets(sheet_url: str):
    client = get_client()
    sheet = client.open_by_url(sheet_url)
    return [ws.title for ws in sheet.worksheets()]


def load_worksheet(sheet_url: str, worksheet_name: str):
    client = get_client()
    sheet = client.open_by_url(sheet_url)
    ws = sheet.worksheet(worksheet_name)
    values = ws.get_all_values()
    return _rows_to_dataframe(values)


def load_multiple_worksheets(sheet_url: str, worksheet_names: list):
    dfs = []

    for name in worksheet_names:
        try:
            df = load_worksheet(sheet_url, name)
        except Exception:
            continue

        if df.empty:
            continue

        df["Date"] = name
        dfs.append(df)

    if not dfs:
        return pd.DataFrame()

    return pd.concat(dfs, ignore_index=True)