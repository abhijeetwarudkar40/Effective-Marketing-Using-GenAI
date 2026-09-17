from pathlib import Path
import pandas as pd
import numpy as np


RAW_DIR = Path("data/raw")


def load_data():
    files = {
        "customers": "customers.csv",
        "transactions": "transactions.csv",
        "product_holdings": "product_holdings.csv",
        "products": "products.csv",
        "campaigns": "campaigns.csv",
        "campaign_interactions": "campaign_interactions.csv",
        "recommendations": "recommendations.csv",
    }

    data = {}

    for name, filename in files.items():
        path = RAW_DIR / filename

        if not path.exists():
            raise FileNotFoundError(f"Missing file: {path}")

        data[name] = pd.read_csv(path)

    return data


def check_basic_quality(data):
    print("\n" + "=" * 70)
    print("1. BASIC DATA QUALITY")
    print("=" * 70)

    for name, df in data.items():
        print(f"\n{name.upper()}")
        print("-" * 50)
        print(f"Rows       : {len(df):,}")
        print(f"Columns    : {len(df.columns)}")
        print(f"Duplicates : {df.duplicated().sum():,}")
        print(f"Missing    : {df.isna().sum().sum():,}")

        if "customer_id" in df.columns:
            print(
                f"Unique customers: "
                f"{df['customer_id'].nunique():,}"
            )


def check_customer_distribution(customers):
    print("\n" + "=" * 70)
    print("2. CUSTOMER DISTRIBUTION")
    print("=" * 70)

    numeric_cols = [
        "age",
        "customer_tenure_years",
        "annual_income",
        "average_account_balance",
        "monthly_spending",
        "transaction_count",
        "average_transaction_amount",
        "recency_days",
        "digital_usage_score",
        "products_held",
        "engagement_score",
        "spending_trend",
    ]

    available = [
        c for c in numeric_cols
        if c in customers.columns
    ]

    print(
        customers[available]
        .describe()
        .round(2)
        .to_string()
    )


def check_business_rules(customers, transactions, holdings):
    print("\n" + "=" * 70)
    print("3. BUSINESS RULE VALIDATION")
    print("=" * 70)

    checks = {}

    checks["negative income"] = (
        customers["annual_income"] < 0
    ).sum()

    checks["negative balance"] = (
        customers["average_account_balance"] < 0
    ).sum()

    checks["negative spending"] = (
        customers["monthly_spending"] < 0
    ).sum()

    checks["invalid digital score"] = (
        (customers["digital_usage_score"] < 0)
        | (customers["digital_usage_score"] > 1)
    ).sum()

    checks["invalid engagement score"] = (
        (customers["engagement_score"] < 0)
        | (customers["engagement_score"] > 1)
    ).sum()

    checks["invalid recency"] = (
        customers["recency_days"] < 0
    ).sum()

    checks["invalid product count"] = (
        customers["products_held"] < 0
    ).sum()

    checks["invalid transaction amount"] = (
        transactions["amount"] <= 0
    ).sum()

    for name, value in checks.items():
        status = "PASS" if value == 0 else "WARNING"
        print(f"{status:8} {name:<35} {value:,}")


def check_relationships(data):
    print("\n" + "=" * 70)
    print("4. RELATIONSHIP / REFERENTIAL INTEGRITY")
    print("=" * 70)

    customers = data["customers"]
    transactions = data["transactions"]
    holdings = data["product_holdings"]
    interactions = data["campaign_interactions"]
    recommendations = data["recommendations"]

    customer_ids = set(customers["customer_id"])

    invalid_transactions = (
        ~transactions["customer_id"].isin(customer_ids)
    ).sum()

    invalid_holdings = (
        ~holdings["customer_id"].isin(customer_ids)
    ).sum()

    invalid_interactions = (
        ~interactions["customer_id"].isin(customer_ids)
    ).sum()

    invalid_recommendations = (
        ~recommendations["customer_id"].isin(customer_ids)
    ).sum()

    print(
        f"Transactions with unknown customer : "
        f"{invalid_transactions:,}"
    )

    print(
        f"Holdings with unknown customer     : "
        f"{invalid_holdings:,}"
    )

    print(
        f"Interactions with unknown customer : "
        f"{invalid_interactions:,}"
    )

    print(
        f"Recommendations with unknown customer: "
        f"{invalid_recommendations:,}"
    )

    product_ids = set(data["products"]["product_id"])

    invalid_product_holdings = (
        ~holdings["product_id"].isin(product_ids)
    ).sum()

    invalid_recommendation_products = (
        ~recommendations["product_id"].isin(product_ids)
    ).sum()

    print(
        f"Holdings with unknown product      : "
        f"{invalid_product_holdings:,}"
    )

    print(
        f"Recommendations with unknown product: "
        f"{invalid_recommendation_products:,}"
    )

    campaign_ids = set(data["campaigns"]["campaign_id"])

    invalid_campaign_interactions = (
        ~interactions["campaign_id"].isin(campaign_ids)
    ).sum()

    print(
        f"Interactions with unknown campaign : "
        f"{invalid_campaign_interactions:,}"
    )


def check_realism(customers):
    print("\n" + "=" * 70)
    print("5. REALISM CHECKS")
    print("=" * 70)

    customers = customers.copy()

    customers["spending_income_ratio"] = (
        customers["monthly_spending"]
        / (customers["annual_income"] / 12)
    )

    print("\nSpending / Monthly Income Ratio")
    print(
        customers["spending_income_ratio"]
        .describe()
        .round(2)
        .to_string()
    )

    print("\nCustomers by Recency Bucket")

    recency_bins = [-1, 7, 30, 90, 365]
    recency_labels = [
        "Active <=7d",
        "Recently Active 8-30d",
        "At Risk 31-90d",
        "Dormant >90d",
    ]

    # Since this synthetic dataset caps recency at 60 days,
    # the last bucket may naturally be zero.
    buckets = pd.cut(
        customers["recency_days"],
        bins=recency_bins,
        labels=recency_labels
    )

    print(
        buckets
        .value_counts()
        .sort_index()
        .to_string()
    )

    print("\nProduct Ownership Distribution")

    print(
        customers["products_held"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    print("\nDigital Usage Distribution")

    print(
        customers["digital_usage_score"]
        .describe()
        .round(3)
        .to_string()
    )

    print("\nIncome vs Balance Correlation")

    print(
        customers[
            [
                "annual_income",
                "average_account_balance",
            ]
        ]
        .corr()
        .round(3)
        .to_string()
    )

    print("\nIncome vs Spending Correlation")

    print(
        customers[
            [
                "annual_income",
                "monthly_spending",
            ]
        ]
        .corr()
        .round(3)
        .to_string()
    )

    print("\nDigital Usage vs Engagement Correlation")

    print(
        customers[
            [
                "digital_usage_score",
                "engagement_score",
            ]
        ]
        .corr()
        .round(3)
        .to_string()
    )


def check_transaction_behavior(customers, transactions):
    print("\n" + "=" * 70)
    print("6. TRANSACTIONAL BEHAVIOR")
    print("=" * 70)

    transaction_summary = (
        transactions
        .groupby("customer_id")
        .agg(
            actual_transactions=("transaction_id", "count"),
            actual_total_amount=("amount", "sum"),
            actual_avg_amount=("amount", "mean"),
        )
    )

    merged = customers[
        [
            "customer_id",
            "transaction_count",
            "monthly_spending",
        ]
    ].merge(
        transaction_summary,
        on="customer_id",
        how="left"
    )

    merged = merged.fillna(0)

    print("\nTransaction Count Comparison")

    print(
        merged[
            [
                "transaction_count",
                "actual_transactions",
            ]
        ]
        .describe()
        .round(2)
        .to_string()
    )

    print("\nActual Transaction Amount")

    print(
        merged["actual_total_amount"]
        .describe()
        .round(2)
        .to_string()
    )

    print("\nTransaction Count Correlation")

    print(
        merged[
            [
                "transaction_count",
                "actual_transactions",
            ]
        ]
        .corr()
        .round(3)
        .to_string()
    )


def main():
    print("=" * 70)
    print("PHASE 1 - RAW DATA QUALITY & BUSINESS VALIDATION")
    print("=" * 70)

    data = load_data()

    check_basic_quality(data)

    check_customer_distribution(
        data["customers"]
    )

    check_business_rules(
        data["customers"],
        data["transactions"],
        data["product_holdings"]
    )

    check_relationships(data)

    check_realism(
        data["customers"]
    )

    check_transaction_behavior(
        data["customers"],
        data["transactions"]
    )

    print("\n" + "=" * 70)
    print("VALIDATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()