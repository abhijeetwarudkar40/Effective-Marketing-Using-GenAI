import pandas as pd


DATA_PATH = (
    "data/processed/customer_clusters.csv"
)


def main():

    print("=" * 70)
    print("PHASE 3D - CLUSTER PROFILING")
    print("=" * 70)

    df = pd.read_csv(DATA_PATH)

    # ---------------------------------------------------------
    # IMPORTANT BUSINESS FEATURES
    # ---------------------------------------------------------

    profile_features = [

        "annual_income",
        "average_account_balance",
        "monthly_spending",

        "transaction_count",
        "average_transaction_amount",
        "recency_days",

        "digital_usage_score",

        "products_held",
        "product_categories_held",

        "engagement_score",

        "average_suitability_score",
        "recommendation_acceptance_rate",

        "debit_ratio",
        "credit_ratio",

        "spending_trend"
    ]

    profile_features = [
        f
        for f in profile_features
        if f in df.columns
    ]

    # ---------------------------------------------------------
    # CLUSTER PROFILE
    # ---------------------------------------------------------

    profile = (
        df
        .groupby("cluster_id")[profile_features]
        .mean()
        .round(2)
    )

    print("\n" + "=" * 70)
    print("CLUSTER BEHAVIOR PROFILE")
    print("=" * 70)

    print(profile.to_string())

    # ---------------------------------------------------------
    # CLUSTER SIZE
    # ---------------------------------------------------------

    sizes = (
        df["cluster_id"]
        .value_counts()
        .sort_index()
        .rename("customer_count")
    )

    percentages = (
        sizes / len(df) * 100
    ).round(2)

    summary = pd.concat(
        [
            sizes,
            percentages.rename(
                "percentage"
            )
        ],
        axis=1
    )

    print("\n" + "=" * 70)
    print("CLUSTER DISTRIBUTION")
    print("=" * 70)

    print(summary.to_string())

    # ---------------------------------------------------------
    # SAVE PROFILE
    # ---------------------------------------------------------

    profile.to_csv(
        "data/processed/cluster_profiles.csv"
    )

    summary.to_csv(
        "data/processed/cluster_sizes.csv"
    )

    print(
        "\nProfile saved to:"
        "\ndata/processed/cluster_profiles.csv"
    )


if __name__ == "__main__":
    main()