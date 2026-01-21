import pandas as pd
from io import BytesIO

def export_excel(well_df, agg_df, well_pivot, agg_pivot):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        well_df.to_excel(writer, sheet_name="Well Level LOS", index=False)
        agg_df.to_excel(writer, sheet_name="Aggregated LOS", index=False)
        well_pivot.to_excel(writer, sheet_name="Well LOS Pivoted", index=False)
        agg_pivot.to_excel(writer, sheet_name="Aggregated LOS Pivoted", index=False)
    output.seek(0)
    return output.read()
