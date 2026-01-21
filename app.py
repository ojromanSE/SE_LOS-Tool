import streamlit as st
import pandas as pd
import tempfile
import os

from parsers.energylink_parser import (
    parse_jib,
    parse_revenue,
    parse_taxes
)
from transforms.los_builder import build_los
from transforms.pivots import pivot_months
from utils.excel_export import export_excel

st.set_page_config(page_title="EnergyLink LOS Builder", layout="wide")

st.title("📊 EnergyLink LOS Builder")

st.markdown("""
Upload **JIB PDFs** and **Revenue PDFs** from EnergyLink.  
The app will generate a **well-level LOS**, **aggregated LOS**, and **pivoted outputs**.
""")

jib_files = st.file_uploader("Upload JIB PDFs", accept_multiple_files=True)
rev_files = st.file_uploader("Upload Revenue PDFs", accept_multiple_files=True)

if st.button("Build LOS"):

    with st.spinner("Parsing PDFs and building LOS..."):

        loe_records = []
        revenue_records = []
        tax_records = []

        with tempfile.TemporaryDirectory() as tmpdir:

            # Save uploaded files locally
            jib_paths = []
            for f in jib_files:
                path = os.path.join(tmpdir, f.name)
                with open(path, "wb") as out:
                    out.write(f.read())
                jib_paths.append(path)

            rev_paths = []
            for f in rev_files:
                path = os.path.join(tmpdir, f.name)
                with open(path, "wb") as out:
                    out.write(f.read())
                rev_paths.append(path)

            # Parse JIBs
            for p in jib_paths:
                loe_records.extend(parse_jib(p))

            # Parse Revenue + Taxes
            for p in rev_paths:
                revenue_records.extend(parse_revenue(p))
                tax_records.extend(parse_taxes(p))

        loe_df = pd.DataFrame(loe_records)
        rev_df = pd.DataFrame(revenue_records)
        tax_df = pd.DataFrame(tax_records)

        los_df = build_los(loe_df, rev_df, tax_df)

        agg_df = (
            los_df
            .groupby("month", as_index=False)
            .sum(numeric_only=True)
        )

        well_pivot = pivot_months(los_df)
        agg_pivot = pivot_months(agg_df, index_cols=["metric"])

        excel_bytes = export_excel(
            los_df,
            agg_df,
            well_pivot,
            agg_pivot
        )

    st.success("LOS built successfully")

    st.download_button(
        label="⬇️ Download LOS Excel",
        data=excel_bytes,
        file_name="LOS_Output.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
