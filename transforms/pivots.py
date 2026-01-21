def pivot_months(df, index_cols=["well", "metric"]):
    long = df.melt(
        id_vars=[c for c in df.columns if c in ["well", "month"]],
        var_name="metric",
        value_name="value"
    )

    pivot = (
        long
        .pivot_table(
            index=["well", "metric"],
            columns="month",
            values="value",
            aggfunc="sum"
        )
        .reset_index()
    )

    return pivot
