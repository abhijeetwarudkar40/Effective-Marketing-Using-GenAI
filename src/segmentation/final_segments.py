from pathlib import Path

import numpy as np
import pandas as pd


PROCESSED_DIR = Path("data/processed")

FEATURES_FILE = PROCESSED_DIR / "customer_features.csv"
CLUSTERS_FILE = PROCESSED_DIR / "customer_clusters.csv"
OUTPUT_FILE = PROCESSED_DIR / "customer_segments.csv"


# ================================================================
# HELPERS
# ================================================================

def percentile_rank(series):
    return series.rank(pct=True)


# ================================================================
# LOAD
# ================================================================

print("=" * 70)
print("PHASE 3F - BUSINESS SEGMENT & BEHAVIORAL ATTRIBUTES")
print("=" * 70)

features = pd.read_csv(FEATURES_FILE)
clusters = pd.read_csv(CLUSTERS_FILE)

print()
print(f"Customers loaded : {len(features):,}")


# ================================================================
# REQUIRED COLUMNS
# ================================================================

required_columns = [
    "customer_id",
    "annual_income",
    "average_account_balance",
    "monthly_spending",
    "transaction_count",
    "recency_days",
    "digital_usage_score",
    "products_held",
    "engagement_score",
    "spending_trend",
    "campaign_open_rate",
    "campaign_click_rate",
    "campaign_conversion_rate",
    "average_suitability_score",
    "recommendation_acceptance_rate",
    "recommendation_conversion_rate",
]

missing = [
    col for col in required_columns
    if col not in features.columns
]

if missing:
    print()
    print("ERROR - Missing columns:")
    for col in missing:
        print(f"  - {col}")

    print()
    print("Available columns:")
    for col in features.columns:
        print(f"  - {col}")

    raise ValueError(
        "customer_features.csv does not contain the required columns."
    )


# ================================================================
# MERGE CLUSTERS
# ================================================================

if "cluster_id" not in clusters.columns:
    raise ValueError(
        "customer_clusters.csv must contain cluster_id."
    )

cluster_data = clusters[
    ["customer_id", "cluster_id"]
].copy()

data = features.merge(
    cluster_data,
    on="customer_id",
    how="left"
)

if data["cluster_id"].isna().any():
    raise ValueError(
        "Some customers do not have cluster assignments."
    )

data["cluster_id"] = data["cluster_id"].astype(int)


# ================================================================
# PRIMARY BUSINESS SEGMENT
# ================================================================

cluster_segment_map = {
    0: "Dormant / Declining",
    1: "Core Active",
    2: "At Risk",
    3: "Premium High-Value",
}

data["primary_segment"] = data[
    "cluster_id"
].map(cluster_segment_map)

if data["primary_segment"].isna().any():
    unknown_clusters = sorted(
        data.loc[
            data["primary_segment"].isna(),
            "cluster_id"
        ].unique()
    )

    raise ValueError(
        f"Unexpected cluster IDs: {unknown_clusters}"
    )


# ================================================================
# CUSTOMER VALUE
# ================================================================

print("Calculating customer value...")

data["income_percentile"] = percentile_rank(
    data["annual_income"]
)

data["balance_percentile"] = percentile_rank(
    data["average_account_balance"]
)

data["spending_percentile"] = percentile_rank(
    data["monthly_spending"]
)

data["transaction_percentile"] = percentile_rank(
    data["transaction_count"]
)

data["customer_value_score"] = (
    0.35 * data["income_percentile"]
    + 0.35 * data["balance_percentile"]
    + 0.20 * data["spending_percentile"]
    + 0.10 * data["transaction_percentile"]
).clip(0, 1)


def value_band(score):
    if score >= 0.80:
        return "Very High"
    elif score >= 0.60:
        return "High"
    elif score >= 0.35:
        return "Medium"
    return "Low"


data["value_band"] = data[
    "customer_value_score"
].apply(value_band)


# ================================================================
# DIGITAL AFFINITY
# ================================================================

print("Calculating digital affinity...")

data["digital_affinity_score"] = (
    0.60 * data["digital_usage_score"]
    + 0.40 * data["engagement_score"]
).clip(0, 1)


def digital_band(score):
    if score >= 0.70:
        return "Highly Digital"
    elif score >= 0.45:
        return "Digitally Active"
    elif score >= 0.25:
        return "Moderate Digital"
    return "Low Digital"


data["digital_affinity"] = data[
    "digital_affinity_score"
].apply(digital_band)


# ================================================================
# TRANSACTIONAL BEHAVIOR
# ================================================================

print("Calculating transactional behavior...")

data["transaction_intensity_score"] = (
    0.50 * percentile_rank(
        data["transaction_count"]
    )
    + 0.30 * percentile_rank(
        data["monthly_spending"]
    )
    + 0.20 * percentile_rank(
        data["average_transaction_amount"]
        if "average_transaction_amount"
        in data.columns
        else data["monthly_spending"]
    )
).clip(0, 1)


def transaction_band(score):
    if score >= 0.75:
        return "Very High Transactional"
    elif score >= 0.50:
        return "High Transactional"
    elif score >= 0.25:
        return "Moderate Transactional"
    return "Low Transactional"


data["transactional_behavior"] = data[
    "transaction_intensity_score"
].apply(transaction_band)


# ================================================================
# ENGAGEMENT
# ================================================================

print("Calculating engagement...")

def engagement_band(score):
    if score >= 0.70:
        return "Very High Engagement"
    elif score >= 0.50:
        return "High Engagement"
    elif score >= 0.30:
        return "Moderate Engagement"
    return "Low Engagement"


data["engagement_level"] = data[
    "engagement_score"
].apply(engagement_band)


# ================================================================
# RELATIONSHIP STATUS
# ================================================================

print("Calculating relationship status...")


def relationship_status(days):
    if days <= 7:
        return "Recently Active"
    elif days <= 30:
        return "Active"
    elif days <= 90:
        return "At Risk"
    else:
        return "Dormant"


data["relationship_status"] = data[
    "recency_days"
].apply(relationship_status)


# ================================================================
# SPENDING BEHAVIOR
# ================================================================

print("Calculating spending behavior...")


def spending_behavior(value):
    if value >= 0.10:
        return "Growing Spender"
    elif value <= -0.10:
        return "Declining Spender"
    return "Stable Spender"


data["spending_behavior"] = data[
    "spending_trend"
].apply(spending_behavior)


# ================================================================
# PRODUCT RELATIONSHIP
# ================================================================

print("Calculating product relationship...")


def relationship_depth(products):
    if products >= 5:
        return "Deep Relationship"
    elif products >= 3:
        return "Established Relationship"
    elif products >= 2:
        return "Developing Relationship"
    return "Shallow Relationship"


data["relationship_depth"] = data[
    "products_held"
].apply(relationship_depth)


# ================================================================
# CROSS-SELL OPPORTUNITY
# ================================================================

print("Calculating cross-sell opportunity...")

product_gap_score = (
    1 - percentile_rank(data["products_held"])
)

activity_score = (
    1 - percentile_rank(data["recency_days"])
)

data["cross_sell_score"] = (
    0.30 * data["customer_value_score"]
    + 0.25 * product_gap_score
    + 0.20 * data["digital_affinity_score"]
    + 0.15 * data["engagement_score"]
    + 0.10 * activity_score
).clip(0, 1)


def cross_sell_band(score):
    if score >= 0.70:
        return "High Cross-Sell Opportunity"
    elif score >= 0.45:
        return "Moderate Cross-Sell Opportunity"
    return "Low Cross-Sell Opportunity"


data["cross_sell_opportunity"] = data[
    "cross_sell_score"
].apply(cross_sell_band)


# ================================================================
# RETENTION RISK
# ================================================================

print("Calculating retention risk...")

recency_risk = percentile_rank(
    data["recency_days"]
)

transaction_risk = (
    1 - percentile_rank(
        data["transaction_count"]
    )
)

engagement_risk = (
    1 - percentile_rank(
        data["engagement_score"]
    )
)

spending_risk = (
    data["spending_trend"] < 0
).astype(float)

data["retention_risk_score"] = (
    0.40 * recency_risk
    + 0.25 * transaction_risk
    + 0.20 * engagement_risk
    + 0.15 * spending_risk
).clip(0, 1)


def retention_band(score):
    if score >= 0.75:
        return "Critical Risk"
    elif score >= 0.55:
        return "High Risk"
    elif score >= 0.35:
        return "Moderate Risk"
    return "Low Risk"


data["retention_risk"] = data[
    "retention_risk_score"
].apply(retention_band)


# ================================================================
# CAMPAIGN RESPONSIVENESS
# ================================================================

print("Calculating marketing responsiveness...")

data["marketing_response_score"] = (
    0.35 * data["campaign_open_rate"]
    + 0.30 * data["campaign_click_rate"]
    + 0.35 * data["campaign_conversion_rate"]
).clip(0, 1)


def marketing_response(score):
    if score >= 0.60:
        return "Highly Responsive"
    elif score >= 0.35:
        return "Responsive"
    elif score >= 0.15:
        return "Low Response"
    return "Unresponsive"


data["marketing_responsiveness"] = data[
    "marketing_response_score"
].apply(marketing_response)


# ================================================================
# RECOMMENDATION READINESS
# ================================================================

print("Calculating recommendation readiness...")

data["recommendation_readiness_score"] = (
    0.35 * data["average_suitability_score"]
    + 0.35 * data["recommendation_acceptance_rate"]
    + 0.30 * data["recommendation_conversion_rate"]
).clip(0, 1)


def recommendation_readiness(score):
    if score >= 0.65:
        return "Highly Ready"
    elif score >= 0.40:
        return "Ready"
    elif score >= 0.20:
        return "Needs Nurturing"
    return "Low Readiness"


data["recommendation_readiness"] = data[
    "recommendation_readiness_score"
].apply(
    recommendation_readiness
)


# ================================================================
# GENAI TARGETING PRIORITY
# ================================================================

print("Calculating GenAI targeting priority...")

priority_score = (
    0.30 * data["cross_sell_score"]
    + 0.25 * data["recommendation_readiness_score"]
    + 0.20 * data["marketing_response_score"]
    + 0.15 * data["customer_value_score"]
    + 0.10 * (
        1 - data["retention_risk_score"]
    )
).clip(0, 1)

data["genai_priority_score"] = priority_score


def targeting_priority(score):
    if score >= 0.75:
        return "Priority 1"
    elif score >= 0.50:
        return "Priority 2"
    elif score >= 0.30:
        return "Priority 3"
    return "Priority 4"


data["genai_targeting_priority"] = data[
    "genai_priority_score"
].apply(targeting_priority)


# ================================================================
# CUSTOMER PERSONA
# ================================================================

print("Generating customer personas...")


def create_persona(row):

    if row["primary_segment"] == "Premium High-Value":

        if row["digital_affinity"] == "Highly Digital":
            return "Premium Digital Customer"

        if row["cross_sell_opportunity"] == (
            "High Cross-Sell Opportunity"
        ):
            return "Premium Cross-Sell Opportunity"

        return "Premium Relationship Customer"

    if row["primary_segment"] == "Dormant / Declining":

        if row["retention_risk"] == "Critical Risk":
            return "Dormant Reactivation Target"

        return "Declining Customer"

    if row["primary_segment"] == "At Risk":

        if row["spending_behavior"] == "Declining Spender":
            return "At-Risk Declining Customer"

        return "At-Risk Engagement Customer"

    # Core Active

    if row["cross_sell_opportunity"] == (
        "High Cross-Sell Opportunity"
    ):
        return "Core Cross-Sell Opportunity"

    if row["digital_affinity"] == "Highly Digital":
        return "Core Digital Customer"

    if row["transactional_behavior"] == (
        "Very High Transactional"
    ):
        return "Core High-Activity Customer"

    return "Core Relationship Customer"


data["customer_persona"] = data.apply(
    create_persona,
    axis=1
)


# ================================================================
# GENAI CONTEXT
# ================================================================

data["recommendation_context"] = (
    data["primary_segment"]
    + " | "
    + data["customer_persona"]
    + " | "
    + data["value_band"]
    + " Value | "
    + data["digital_affinity"]
    + " | "
    + data["transactional_behavior"]
    + " | "
    + data["spending_behavior"]
    + " | "
    + data["relationship_depth"]
    + " | "
    + data["cross_sell_opportunity"]
    + " | "
    + data["retention_risk"]
    + " | "
    + data["recommendation_readiness"]
)


# ================================================================
# FINAL OUTPUT
# ================================================================

output_columns = [
    "customer_id",

    "cluster_id",
    "primary_segment",
    "customer_persona",

    "customer_value_score",
    "value_band",

    "transaction_intensity_score",
    "transactional_behavior",

    "digital_affinity_score",
    "digital_affinity",

    "engagement_level",

    "relationship_status",
    "relationship_depth",

    "spending_behavior",

    "marketing_response_score",
    "marketing_responsiveness",

    "cross_sell_score",
    "cross_sell_opportunity",

    "retention_risk_score",
    "retention_risk",

    "recommendation_readiness_score",
    "recommendation_readiness",

    "genai_priority_score",
    "genai_targeting_priority",

    "recommendation_context",
]

output = data[output_columns].copy()


# ================================================================
# VALIDATION
# ================================================================

print()
print("=" * 70)
print("FINAL BUSINESS SEGMENT DISTRIBUTION")
print("=" * 70)

segment_distribution = (
    output["primary_segment"]
    .value_counts()
    .rename_axis("primary_segment")
    .reset_index(name="customers")
)

segment_distribution["percentage"] = (
    segment_distribution["customers"]
    / len(output)
    * 100
)

print(
    segment_distribution.to_string(
        index=False,
        formatters={
            "percentage": "{:.2f}".format
        }
    )
)


print()
print("=" * 70)
print("CUSTOMER PERSONA DISTRIBUTION")
print("=" * 70)

print(
    output["customer_persona"]
    .value_counts()
    .to_string()
)


print()
print("=" * 70)
print("RETENTION RISK DISTRIBUTION")
print("=" * 70)

print(
    output["retention_risk"]
    .value_counts()
    .to_string()
)


print()
print("=" * 70)
print("CROSS-SELL OPPORTUNITY")
print("=" * 70)

print(
    output["cross_sell_opportunity"]
    .value_counts()
    .to_string()
)


print()
print("=" * 70)
print("GENAI PRIORITY")
print("=" * 70)

print(
    output["genai_targeting_priority"]
    .value_counts()
    .sort_index()
    .to_string()
)


# ================================================================
# SAVE
# ================================================================

output.to_csv(
    OUTPUT_FILE,
    index=False
)

print()
print("=" * 70)
print("PHASE 3F COMPLETE")
print("=" * 70)

print()
print("Saved to:")
print(OUTPUT_FILE)

print()
print(f"Rows    : {len(output):,}")
print(f"Columns : {len(output.columns):,}")