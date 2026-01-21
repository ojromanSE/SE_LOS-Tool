import pandas as pd


def _ensure_columns(df, required_cols):
    """
    Ensure DataFrame has required columns.
    If df is empty or missing columns, add them with zeros.
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=required_cols)

    for col in required_cols:
        if col not in df.columns:
            df[col] = 0.0

    return df


def build_los(loe_df, rev_df, tax_df):
    """
    Build well-level LOS safely, even with missing / partial data
    """

    # -------------------------
    # Normalize inputs
    # -------------------------

    loe_df = _ensure_columns(
        loe_df,
        ["well", "month", "loe"]
    )

    rev_df = _ensure_columns(
        rev_df,
        [
            "well",
            "month",
            "oil_volume",
            "oil_revenue",
            "gas_volume",
            "gas_revenue",
            "ngl_volume",
            "ngl_revenue",
        ]
    )

    tax_df = _ensure_columns(
        tax_df,
        ["well", "month", "tax"]
    )

    # -------------------------
    # Merge datasets
    # -------------------------

    df = pd.merge(
        loe_df,
        rev_df,
        on=["well", "month"],
        how="outer"
    )

    df = pd.merge(
        df,
        tax_df,
        on=["well", "month"],
        how="left"
    )

    # -------------------------
    # Fill missing values
    # -------------------------

    numeric_cols = [
        "loe",
        "oil_volume",
        "oil_revenue",
        "gas_volume",
        "gas_revenue",
        "ngl_volume",
        "ngl_revenue",
        "tax",
    ]

    for col in numeric_cols:
        if col not in df.columns:
            df[col] = 0.0
        df[col] = df[col].fillna(0.0)

    # -------------------------
    # LOS Calculations
    # -------------------------

    df["total_revenue"] = (
        df["oil_revenue"]
        + df["gas_revenue"]
        + df["ngl_revenue"]
    )

    df
