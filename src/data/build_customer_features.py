from pathlib import Path

import numpy as np
import pandas as pd


# ================================================================
# CONFIGURATION
# ================================================================

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

REFERENCE_DATE = pd.Timestamp("2026-08-29")


# ================================================================
# HELPERS
# ================================================================

def safe_divide(numerator, denominator):
    return numerator / denominator.replace(0, np.nan)


def load_csv(filename):
    path = RAW_DIR / filename

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    return pd.read_csv(path)


# ================================================================
# LOAD RAW DATA
# ================================================================

print("=" * 70)
print("PHASE 2 - CUSTOMER FEATURE ENGINEERING")
print("=" * 70)
print()
print("Loading raw datasets...")

customers = load_csv("customers.csv")
transactions = load_csv("transactions.csv")
product_holdings = load_csv("product_holdings.csv")
products = load_csv("products.csv")
campaigns = load_csv("campaigns.csv")
campaign_interactions = load_csv("campaign_interactions.csv")
recommendations = load_csv("recommendations.csv")

print(f"Customers              : {len(customers):,}")
print(f"Transactions            : {len(transactions):,}")
print(f"Product holdings        : {len(product_holdings):,}")
print(f"Products                : {len(products):,}")
print(f"Campaigns               : {len(campaigns):,}")
print(f"Campaign interactions   : {len(campaign_interactions):,}")
print(f"Recommendations         : {len(recommendations):,}")
print()


# ================================================================
# DATE CONVERSION
# ================================================================

transactions["transaction_date"] = pd.to_datetime(
    transactions["transaction_date"]
)

campaign_interactions["interaction_date"] = pd.to_datetime(
    campaign_interactions["interaction_date"]
)

recommendations["recommendation_date"] = pd.to_datetime(
    recommendations["recommendation_date"]
)


# ================================================================
# 1. TRANSACTION FEATURES
# ================================================================

print("Building transaction features...")

transaction_features = (
    transactions
    .groupby("customer_id")
    .agg(
        total_transaction_amount=("amount", "sum"),
        average_transaction_amount=("amount", "mean"),
        median_transaction_amount=("amount", "median"),
        transaction_count_actual=("transaction_id", "count"),
        active_months=(
            "transaction_date",
            lambda x: x.dt.to_period("M").nunique()
        ),
        last_transaction_date=("transaction_date", "max"),
        first_transaction_date=("transaction_date", "min"),
        debit_transactions=(
            "transaction_type",
            lambda x: (x == "Debit").sum()
        ),
        credit_transactions=(
            "transaction_type",
            lambda x: (x == "Credit").sum()
        ),
        transaction_amount_std=("amount", "std"),
    )
    .reset_index()
)

transaction_features["transaction_amount_std"] = (
    transaction_features["transaction_amount_std"]
    .fillna(0)
)

transaction_features["transactions_per_active_month"] = (
    transaction_features["transaction_count_actual"]
    /
    transaction_features["active_months"].replace(0, np.nan)
).fillna(0)

transaction_features["debit_ratio_actual"] = (
    transaction_features["debit_transactions"]
    /
    transaction_features["transaction_count_actual"]
    .replace(0, np.nan)
).fillna(0)

transaction_features["credit_ratio_actual"] = (
    transaction_features["credit_transactions"]
    /
    transaction_features["transaction_count_actual"]
    .replace(0, np.nan)
).fillna(0)


# ================================================================
# 2. RFM FEATURES
# ================================================================

print("Building RFM features...")

rfm = (
    transactions
    .groupby("customer_id")
    .agg(
        last_transaction_date=("transaction_date", "max"),
        frequency=("transaction_id", "count"),
        monetary=("amount", "sum"),
    )
    .reset_index()
)

rfm["recency_days_actual"] = (
    REFERENCE_DATE - rfm["last_transaction_date"]
).dt.days.clip(lower=0)


# Rank first so qcut works even with repeated values.
rfm["recency_rank"] = rfm["recency_days_actual"].rank(
    method="first",
    ascending=False
)

rfm["frequency_rank"] = rfm["frequency"].rank(
    method="first",
    ascending=True
)

rfm["monetary_rank"] = rfm["monetary"].rank(
    method="first",
    ascending=True
)

rfm["recency_score"] = pd.qcut(
    rfm["recency_rank"],
    5,
    labels=[1, 2, 3, 4, 5]
).astype(int)

rfm["frequency_score"] = pd.qcut(
    rfm["frequency_rank"],
    5,
    labels=[1, 2, 3, 4, 5]
).astype(int)

rfm["monetary_score"] = pd.qcut(
    rfm["monetary_rank"],
    5,
    labels=[1, 2, 3, 4, 5]
).astype(int)

rfm["rfm_score"] = (
    rfm["recency_score"]
    + rfm["frequency_score"]
    + rfm["monetary_score"]
)

rfm = rfm[
    [
        "customer_id",
        "recency_days_actual",
        "frequency",
        "monetary",
        "recency_score",
        "frequency_score",
        "monetary_score",
        "rfm_score",
    ]
]


# ================================================================
# 3. PRODUCT FEATURES
# ================================================================

print("Building product relationship features...")

holdings_enriched = product_holdings.merge(
    products[
        [
            "product_id",
            "category",
            "product_type",
        ]
    ],
    on="product_id",
    how="left",
)

product_features = (
    holdings_enriched
    .groupby("customer_id")
    .agg(
        products_held_actual=("product_id", "nunique"),
        product_categories_held=("category", "nunique"),
        product_value_total=("product_value", "sum"),
        product_value_average=("product_value", "mean"),
        loan_products=(
            "product_type",
            lambda x: (x == "Loan").sum()
        ),
        investment_products=(
            "product_type",
            lambda x: (x == "Investment").sum()
        ),
        insurance_products=(
            "product_type",
            lambda x: (x == "Insurance").sum()
        ),
        credit_card_products=(
            "product_type",
            lambda x: (x == "Credit Card").sum()
        ),
    )
    .reset_index()
)


# ================================================================
# 4. CAMPAIGN FEATURES
# ================================================================

print("Building campaign engagement features...")

campaign_features = (
    campaign_interactions
    .groupby("customer_id")
    .agg(
        campaigns_received=("campaign_id", "nunique"),
        campaign_interactions=("campaign_id", "count"),
        campaigns_opened=("opened", "sum"),
        campaigns_clicked=("clicked", "sum"),
        campaigns_converted=("converted", "sum"),
    )
    .reset_index()
)

campaign_features["campaign_open_rate"] = (
    campaign_features["campaigns_opened"]
    /
    campaign_features["campaign_interactions"]
    .replace(0, np.nan)
).fillna(0)

campaign_features["campaign_click_rate"] = (
    campaign_features["campaigns_clicked"]
    /
    campaign_features["campaigns_opened"]
    .replace(0, np.nan)
).fillna(0)

campaign_features["campaign_conversion_rate"] = (
    campaign_features["campaigns_converted"]
    /
    campaign_features["campaigns_clicked"]
    .replace(0, np.nan)
).fillna(0)


# ================================================================
# 5. RECOMMENDATION FEATURES
# ================================================================

print("Building recommendation behavior features...")

recommendation_features = (
    recommendations
    .groupby("customer_id")
    .agg(
        recommendations_received=("recommendation_id", "count"),
        average_suitability_score=("suitability_score", "mean"),
        recommendations_accepted=("accepted", "sum"),
        recommendations_converted=("converted", "sum"),
    )
    .reset_index()
)

recommendation_features["recommendation_acceptance_rate"] = (
    recommendation_features["recommendations_accepted"]
    /
    recommendation_features["recommendations_received"]
    .replace(0, np.nan)
).fillna(0)

recommendation_features["recommendation_conversion_rate"] = (
    recommendation_features["recommendations_converted"]
    /
    recommendation_features["recommendations_accepted"]
    .replace(0, np.nan)
).fillna(0)


# ================================================================
# 6. HIGH-VALUE TRANSACTION BEHAVIOR
# ================================================================

print("Building transaction behavior indicators...")

high_value = (
    transactions
    .assign(
        high_value=(transactions["amount"] >= 5000).astype(int)
    )
    .groupby("customer_id")["high_value"]
    .sum()
    .reset_index()
)

high_value = high_value.rename(
    columns={"high_value": "high_value_transactions"}
)


# ================================================================
# 7. MERGE EVERYTHING
# ================================================================

print("Combining customer-level features...")

features = customers.copy()

features = features.merge(
    transaction_features,
    on="customer_id",
    how="left"
)

features = features.merge(
    rfm,
    on="customer_id",
    how="left"
)

features = features.merge(
    product_features,
    on="customer_id",
    how="left"
)

features = features.merge(
    campaign_features,
    on="customer_id",
    how="left"
)

features = features.merge(
    recommendation_features,
    on="customer_id",
    how="left"
)

features = features.merge(
    high_value,
    on="customer_id",
    how="left"
)


# ================================================================
# 8. FILL MISSING AGGREGATIONS
# ================================================================

aggregation_columns = [
    "total_transaction_amount",
    "average_transaction_amount",
    "median_transaction_amount",
    "transaction_count_actual",
    "active_months",
    "debit_transactions",
    "credit_transactions",
    "transactions_per_active_month",
    "debit_ratio_actual",
    "credit_ratio_actual",
    "transaction_amount_std",
    "products_held_actual",
    "product_categories_held",
    "product_value_total",
    "product_value_average",
    "loan_products",
    "investment_products",
    "insurance_products",
    "credit_card_products",
    "campaigns_received",
    "campaign_interactions",
    "campaigns_opened",
    "campaigns_clicked",
    "campaigns_converted",
    "campaign_open_rate",
    "campaign_click_rate",
    "campaign_conversion_rate",
    "recommendations_received",
    "average_suitability_score",
    "recommendations_accepted",
    "recommendations_converted",
    "recommendation_acceptance_rate",
    "recommendation_conversion_rate",
    "high_value_transactions",
]

for column in aggregation_columns:
    if column in features.columns:
        features[column] = features[column].fillna(0)


# ================================================================
# 9. DERIVED BUSINESS FEATURES
# ================================================================

print("Creating derived business features...")

features["monthly_income"] = (
    features["annual_income"] / 12
)

features["balance_to_income_ratio"] = (
    features["average_account_balance"]
    /
    features["annual_income"].replace(0, np.nan)
).fillna(0)

features["spending_to_income_ratio"] = (
    features["monthly_spending"]
    /
    features["monthly_income"].replace(0, np.nan)
).fillna(0)

features["transaction_value_to_income_ratio"] = (
    features["total_transaction_amount"]
    /
    features["annual_income"].replace(0, np.nan)
).fillna(0)

features["product_penetration"] = (
    features["products_held_actual"]
    / len(products)
)

features["high_value_transaction_ratio"] = (
    features["high_value_transactions"]
    /
    features["transaction_count_actual"]
    .replace(0, np.nan)
).fillna(0)

features["digital_activity_index"] = (
    0.45 * features["digital_usage_score"]
    +
    0.25 * features["digital_transaction_ratio"]
    +
    0.30 * (
        features["mobile_app_login_frequency"] / 30
    ).clip(0, 1)
)

features["relationship_depth_score"] = (
    0.40 * (
        features["products_held_actual"] / len(products)
    )
    +
    0.30 * (
        features["active_months"]
        /
        features["active_months"].max()
    )
    +
    0.30 * features["engagement_score"]
)

features["customer_value_index"] = (
    0.40 * features["annual_income"].rank(pct=True)
    +
    0.35 * features["average_account_balance"].rank(pct=True)
    +
    0.25 * features["monthly_spending"].rank(pct=True)
)


# ================================================================
# 10. CLEANUP
# ================================================================

# Remove duplicate date columns created by the merges.
features = features.drop(
    columns=[
        "last_transaction_date_x",
        "last_transaction_date_y",
    ],
    errors="ignore"
)

features = features.sort_values(
    "customer_id"
).reset_index(drop=True)


# ================================================================
# 11. VALIDATION
# ================================================================

print()
print("=" * 70)
print("FEATURE DATASET VALIDATION")
print("=" * 70)

print(f"Customers : {len(features):,}")
print(f"Features  : {len(features.columns):,}")

print(
    f"Duplicate customer IDs : "
    f"{features['customer_id'].duplicated().sum()}"
)

print(
    f"Missing values          : "
    f"{features.isna().sum().sum()}"
)

print()

# ================================================================
# 12. SAVE
# ================================================================

output_path = PROCESSED_DIR / "customer_features.csv"

features.to_csv(
    output_path,
    index=False
)

print("=" * 70)
print("PHASE 2 COMPLETE")
print("=" * 70)
print()
print(f"Saved to:")
print(output_path)
print()
print("Feature groups:")
print("  1. Financial")
print("  2. Transactional")
print("  3. RFM")
print("  4. Spending")
print("  5. Digital")
print("  6. Product relationship")
print("  7. Campaign engagement")
print("  8. Recommendation behavior")
print("  9. Customer value")
print()