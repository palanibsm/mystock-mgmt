from __future__ import annotations

import io
import pandas as pd
import streamlit as st

from db.database import get_holdings, delete_all_holdings, bulk_insert_holdings

st.header("Import / Export Portfolio")
st.caption("Download your holdings as CSV or upload a revised CSV to sync data.")

EXPORT_COLUMNS = [
    "category", "name", "symbol", "quantity", "buy_price",
    "buy_date", "currency", "broker", "notes",
]
REQUIRED_COLUMNS = {"category", "name", "symbol", "quantity", "buy_price", "currency"}

# ────────────────────────── DOWNLOAD ──────────────────────────

st.subheader("Download Holdings")

holdings = get_holdings()

if holdings:
    df_export = pd.DataFrame(holdings)[EXPORT_COLUMNS]
    csv_bytes = df_export.to_csv(index=False).encode("utf-8")

    st.write(f"**{len(df_export)}** holdings across all categories.")
    st.download_button(
        label="Download CSV",
        data=csv_bytes,
        file_name="mystock_portfolio.csv",
        mime="text/csv",
        type="primary",
    )

    with st.expander("Preview export data"):
        st.dataframe(df_export, use_container_width=True, hide_index=True)
else:
    st.info("No holdings to export. Add some holdings first.")

st.markdown("---")

# ────────────────────────── UPLOAD ──────────────────────────

st.subheader("Upload Holdings")
st.warning(
    "Uploading will **replace all existing holdings** with the data from the CSV. "
    "Make sure to download a backup first!"
)

uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file is not None:
    try:
        df_import = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Failed to read CSV: {e}")
        st.stop()

    # Validate required columns
    missing = REQUIRED_COLUMNS - set(df_import.columns)
    if missing:
        st.error(f"CSV is missing required columns: **{', '.join(sorted(missing))}**")
        st.stop()

    # Fill optional columns with empty string
    for col in EXPORT_COLUMNS:
        if col not in df_import.columns:
            df_import[col] = ""

    # Replace NaN with empty string for text fields, 0 for numeric
    df_import["buy_date"] = df_import["buy_date"].fillna("")
    df_import["broker"] = df_import["broker"].fillna("")
    df_import["notes"] = df_import["notes"].fillna("")

    st.write(f"**{len(df_import)}** holdings found in the CSV.")

    with st.expander("Preview import data", expanded=True):
        st.dataframe(df_import[EXPORT_COLUMNS], use_container_width=True, hide_index=True)

    # Confirm import
    if st.button("Replace All Holdings with This Data", type="primary"):
        rows = df_import[EXPORT_COLUMNS].to_dict("records")

        deleted = delete_all_holdings()
        inserted = bulk_insert_holdings(rows)

        st.success(
            f"Done! Removed **{deleted}** old holdings and imported **{inserted}** new holdings."
        )
        st.balloons()
