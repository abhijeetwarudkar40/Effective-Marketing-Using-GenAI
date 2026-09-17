import pandas as pd


DATA_PATH = "data/processed/customer_clusters.csv"


def main():

    print("=" * 70)
    print("PHASE 3E - CLUSTER VALIDATION")
    print("=" * 70)

    df = pd.read_csv(DATA_PATH)

    # ---------------------------------------------------------
    # PRODUCT VALIDATION
    # ---------------------------------------------------------

    print("\nPRODUCT HOLDINGS BY CLUSTER")
    print("-" * 70)

    product_profile = (
        df.groupby("cluster_id")
        .agg(
            customers=("customer_id", "count"),
            avg_products=("products_held", "mean"),
            zero_product_customers=(
                "products_held",
                lambda x: (x == 0).sum()
            ),
            max_products=("products_held", "max")
        )
        .round(2)
    )

    print(product_profile)

    # ---------------------------------------------------------
    # TRANSACTION PROFILE
    # ---------------------------------------------------------

    print("\nTRANSACTION PROFILE")
    print("-" * 70)

    transaction_profile = (
        df.groupby("cluster_id")
        .agg(
            customers=("customer_id", "count"),
            avg_transactions=(
                "transaction_count",
                "mean"
            ),
            median_transactions=(
                "transaction_count",
                "median"
            ),
            avg_spending=(
                "monthly_spending",
                "mean"
            ),
            median_spending=(
                "monthly_spending",
                "median"
            ),
            avg_recency=(
                "recency_days",
                "mean"
            ),
            median_recency=(
                "recency_days",
                "median"
            )
        )
        .round(2)
    )

    print(transaction_profile)

    # ---------------------------------------------------------
    # DIGITAL BEHAVIOR
    # ---------------------------------------------------------

    print("\nDIGITAL BEHAVIOR")
    print("-" * 70)

    digital_profile = (
        df.groupby("cluster_id")
        .agg(
            avg_digital_usage=(
                "digital_usage_score",
                "mean"
            ),
            median_digital_usage=(
                "digital_usage_score",
                "median"
            ),
            avg_engagement=(
                "engagement_score",
                "mean"
            ),
            median_engagement=(
                "engagement_score",
                "median"
            )
        )
        .round(3)
    )

    print(digital_profile)

    # ---------------------------------------------------------
    # CUSTOMER VALUE
    # ---------------------------------------------------------

    print("\nCUSTOMER VALUE")
    print("-" * 70)

    value_profile = (
        df.groupby("cluster_id")
        .agg(
            avg_income=(
                "annual_income",
                "mean"
            ),
            median_income=(
                "annual_income",
                "median"
            ),
            avg_balance=(
                "average_account_balance",
                "mean"
            ),
            median_balance=(
                "average_account_balance",
                "median"
            )
        )
        .round(2)
    )

    print(value_profile)

    # ---------------------------------------------------------
    # CLUSTER 1 CUSTOMER SAMPLE
    # ---------------------------------------------------------

    print("\nCLUSTER 1 - ZERO PRODUCT CUSTOMERS")
    print("-" * 70)

    cluster_1 = df[
        (df["cluster_id"] == 1) &
        (df["products_held"] == 0)
    ]

    columns = [
        "customer_id",
        "annual_income",
        "average_account_balance",
        "monthly_spending",
        "transaction_count",
        "recency_days",
        "digital_usage_score",
        "products_held"
    ]

    columns = [
        c for c in columns
        if c in cluster_1.columns
    ]

    print(
        cluster_1[columns]
        .head(20)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()