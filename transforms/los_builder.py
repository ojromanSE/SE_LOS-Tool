import pandas as pd

def build_los(loe_df, rev_df, tax_df):

    df = loe_df.copy()

    df = df.merge(rev_df, on=["well", "month"], how="outer")
    df = df.merge(tax_df, on=["well", "month"], how="left")

    df = df.fillna(0)

    df["total_revenue"] = (
        df.get("oil_revenue", 0)
        + df.get("gas_revenue", 0)
        + df.get("ngl_revenue", 0)
    )

    df["net_income"] = df["total_revenue"] - df["loe"] - df["tax"]

    return df
