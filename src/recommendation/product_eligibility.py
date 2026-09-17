import pandas as pd
from pathlib import Path


RAW_PATH = Path("data/raw")
PROCESSED_PATH = Path("data/processed")


def load_data():

    features = pd.read_csv(
        PROCESSED_PATH / "customer_features.csv"
    )

    segments = pd.read_csv(
        PROCESSED_PATH / "customer_segments.csv"
    )

    products = pd.read_csv(
        RAW_PATH / "products.csv"
    )

    holdings = pd.read_csv(
        RAW_PATH / "product_holdings.csv"
    )

    return features, segments, products, holdings


def build_product_eligibility():

    print("=" * 70)
    print("PHASE 4A - PRODUCT ELIGIBILITY")
    print("=" * 70)

    features, segments, products, holdings = load_data()

    print(f"\nCustomers : {features['customer_id'].nunique()}")
    print(f"Products  : {products['product_id'].nunique()}")
    print(f"Holdings  : {len(holdings)}")

    # ---------------------------------------------------------
    # 1. Active product holdings
    # ---------------------------------------------------------

    active_holdings = holdings[
        holdings["status"].str.lower() == "active"
    ].copy()

    # Customer -> products already owned
    owned_products = (
        active_holdings
        .groupby("customer_id")["product_id"]
        .apply(set)
        .to_dict()
    )

    # ---------------------------------------------------------
    # 2. Create customer x product combinations
    # ---------------------------------------------------------

    customer_ids = features[
        ["customer_id"]
    ].drop_duplicates()

    product_catalog = products[
        [
            "product_id",
            "product_name",
            "product_type",
            "category",
            "indicative_rate",
            "minimum_value",
            "priority"
        ]
    ].drop_duplicates()

    customer_ids["key"] = 1
    product_catalog["key"] = 1

    eligibility = customer_ids.merge(
        product_catalog,
        on="key"
    ).drop(columns="key")

    # ---------------------------------------------------------
    # 3. Existing ownership
    # ---------------------------------------------------------

    eligibility["already_owned"] = eligibility.apply(
        lambda row:
        row["product_id"]
        in owned_products.get(row["customer_id"], set()),
        axis=1
    )

    # ---------------------------------------------------------
    # 4. Basic eligibility
    # ---------------------------------------------------------

    eligibility["eligible"] = (
        ~eligibility["already_owned"]
    )

    # ---------------------------------------------------------
    # 5. Add customer features
    # ---------------------------------------------------------

    feature_columns = [
        "annual_income",
        "average_account_balance",
        "monthly_spending",
        "transaction_count",
        "recency_days",
        "digital_usage_score",
        "products_held",
        "engagement_score",
        "average_suitability_score",
        "recommendation_acceptance_rate",
        "recommendation_conversion_rate",
        "debit_ratio",
        "credit_ratio",
        "spending_trend"
    ]

    available_features = [
        column
        for column in feature_columns
        if column in features.columns
    ]

    eligibility = eligibility.merge(
        features[
            ["customer_id"] + available_features
        ],
        on="customer_id",
        how="left"
    )

    # ---------------------------------------------------------
    # 6. Add business segmentation
    # ---------------------------------------------------------

    segment_columns = [
        "customer_id",
        "primary_segment",
        "customer_persona",
        "retention_risk",
        "cross_sell_opportunity",
        "genai_targeting_priority"
    ]

    available_segments = [
        column
        for column in segment_columns
        if column in segments.columns
    ]

    eligibility = eligibility.merge(
        segments[available_segments],
        on="customer_id",
        how="left"
    )

    # ---------------------------------------------------------
    # 7. Validation
    # ---------------------------------------------------------

    print("\nELIGIBILITY SUMMARY")
    print("-" * 70)

    total_pairs = len(eligibility)

    owned_count = eligibility[
        "already_owned"
    ].sum()

    eligible_count = eligibility[
        "eligible"
    ].sum()

    print(
        f"Customer-product pairs : {total_pairs}"
    )

    print(
        f"Already owned          : {owned_count}"
    )

    print(
        f"Eligible products      : {eligible_count}"
    )

    eligible_per_customer = (
        eligibility[
            eligibility["eligible"]
        ]
        .groupby("customer_id")
        .size()
    )

    print("\nEligible products per customer:")
    print(
        eligible_per_customer.describe()
    )

    # ---------------------------------------------------------
    # 8. Validation checks
    # ---------------------------------------------------------

    duplicate_pairs = eligibility.duplicated(
        ["customer_id", "product_id"]
    ).sum()

    print(
        f"\nDuplicate customer-product pairs : "
        f"{duplicate_pairs}"
    )

    invalid_ownership = (
        eligibility[
            eligibility["already_owned"]
        ]["eligible"]
        .sum()
    )

    print(
        f"Owned products incorrectly eligible : "
        f"{invalid_ownership}"
    )

    # ---------------------------------------------------------
    # 9. Save
    # ---------------------------------------------------------

    output_path = (
        PROCESSED_PATH /
        "customer_product_eligibility.csv"
    )

    eligibility.to_csv(
        output_path,
        index=False
    )

    print("\nSaved to:")
    print(output_path)

    print("\nPHASE 4A COMPLETE")

    return eligibility


if __name__ == "__main__":
    build_product_eligibility()