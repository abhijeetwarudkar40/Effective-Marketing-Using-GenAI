from pathlib import Path
import pandas as pd
import numpy as np


INPUT_FILE = Path("data/processed/customer_product_eligibility.csv")
OUTPUT_FILE = Path("data/processed/customer_product_scores.csv")


def minmax(series):
    """Robust 0-1 normalization."""
    series = pd.to_numeric(series, errors="coerce").fillna(0)

    min_val = series.min()
    max_val = series.max()

    if max_val == min_val:
        return pd.Series(0.5, index=series.index)

    return (series - min_val) / (max_val - min_val)


def score_product_fit(row):
    """
    Product-specific business suitability score.
    Returns a value between 0 and 1.
    """

    product = row["product_id"]

    income = row["income_score"]
    balance = row["balance_score"]
    spending = row["spending_score"]
    transactions = row["transaction_score"]
    digital = row["digital_score"]
    engagement = row["engagement_score_norm"]
    age = row["age_score"]
    tenure = row["tenure_score"]

    segment = row["primary_segment"]
    persona = row["customer_persona"]

    score = 0.0

    # ---------------------------------------------------------
    # P003 - Rewards Credit Card
    # ---------------------------------------------------------
    if product == "P003":

        score = (
            0.30 * spending
            + 0.25 * transactions
            + 0.20 * digital
            + 0.15 * engagement
            + 0.10 * income
        )

    # ---------------------------------------------------------
    # P004 - Personal Loan
    # ---------------------------------------------------------
    elif product == "P004":

        score = (
            0.30 * income
            + 0.20 * spending
            + 0.20 * transactions
            + 0.15 * balance
            + 0.15 * tenure
        )

    # ---------------------------------------------------------
    # P005 - Home Loan
    # ---------------------------------------------------------
    elif product == "P005":

        score = (
            0.35 * income
            + 0.30 * balance
            + 0.15 * tenure
            + 0.10 * transactions
            + 0.10 * spending
        )

    # ---------------------------------------------------------
    # P006 - Mutual Fund Plan
    # ---------------------------------------------------------
    elif product == "P006":

        score = (
            0.35 * balance
            + 0.25 * income
            + 0.15 * tenure
            + 0.15 * engagement
            + 0.10 * digital
        )

    # ---------------------------------------------------------
    # P007 - Term Insurance
    # ---------------------------------------------------------
    elif product == "P007":

        score = (
            0.30 * income
            + 0.25 * balance
            + 0.20 * age
            + 0.15 * tenure
            + 0.10 * engagement
        )

    # ---------------------------------------------------------
    # P008 - Premium Banking
    # ---------------------------------------------------------
    elif product == "P008":

        score = (
            0.35 * balance
            + 0.25 * income
            + 0.15 * digital
            + 0.15 * engagement
            + 0.10 * tenure
        )

    # Premium segment bonus
    if segment == "Premium High-Value":
        score += 0.05

    # Premium personas
    if "Premium" in str(persona):
        score += 0.03

    return min(score, 1.0)


def main():

    print("=" * 70)
    print("PHASE 4B - CUSTOMER-PRODUCT RECOMMENDATION SCORING")
    print("=" * 70)

    print("\nLoading eligibility data...")

    df = pd.read_csv(INPUT_FILE)

    print(f"Rows loaded : {len(df):,}")
    print(f"Customers   : {df['customer_id'].nunique():,}")
    print(f"Products    : {df['product_id'].nunique():,}")

    # ---------------------------------------------------------
    # Score only eligible products
    # ---------------------------------------------------------

    df["eligible"] = df["eligible"].astype(int)

    eligible = df[df["eligible"] == 1].copy()

    print(f"Eligible pairs : {len(eligible):,}")

    # ---------------------------------------------------------
    # Load additional customer attributes
    # ---------------------------------------------------------

    customer_file = Path(
        "data/processed/customer_features.csv"
    )

    customer_features = pd.read_csv(customer_file)

    # Keep useful fields that may not be in eligibility file
    extra_columns = [
        "customer_id",
        "age",
        "customer_tenure_years",
    ]

    available_extra = [
        c for c in extra_columns
        if c in customer_features.columns
    ]

    customer_features = customer_features[
        available_extra
    ].drop_duplicates("customer_id")

    eligible = eligible.merge(
        customer_features,
        on="customer_id",
        how="left",
        suffixes=("", "_customer")
    )

    # ---------------------------------------------------------
    # Normalized behavioral scores
    # ---------------------------------------------------------

    eligible["income_score"] = minmax(
        eligible["annual_income"]
    )

    eligible["balance_score"] = minmax(
        eligible["average_account_balance"]
    )

    eligible["spending_score"] = minmax(
        eligible["monthly_spending"]
    )

    eligible["transaction_score"] = minmax(
        eligible["transaction_count"]
    )

    eligible["digital_score"] = minmax(
        eligible["digital_usage_score"]
    )

    eligible["engagement_score_norm"] = minmax(
        eligible["engagement_score"]
    )

    eligible["tenure_score"] = minmax(
        eligible["customer_tenure_years"]
    )

    # ---------------------------------------------------------
    # Age suitability
    # ---------------------------------------------------------

    eligible["age"] = pd.to_numeric(
        eligible["age"],
        errors="coerce"
    ).fillna(
        eligible["age"].median()
    )

    # Insurance generally becomes more relevant
    # through the working-age / family-building period.
    eligible["age_score"] = np.clip(
        (eligible["age"] - 21) / (60 - 21),
        0,
        1
    )

    # ---------------------------------------------------------
    # Product-specific suitability
    # ---------------------------------------------------------

    eligible["product_fit_score"] = eligible.apply(
        score_product_fit,
        axis=1
    )

    # ---------------------------------------------------------
    # Historical recommendation behavior
    # ---------------------------------------------------------

    eligible["historical_response_score"] = (
        0.50
        * eligible["recommendation_acceptance_rate"]
        + 0.50
        * eligible["recommendation_conversion_rate"]
    )

    eligible["historical_response_score"] = (
        eligible["historical_response_score"]
        .clip(0, 1)
        .fillna(0)
    )

    # ---------------------------------------------------------
    # Cross-sell opportunity
    # ---------------------------------------------------------

    cross_sell_mapping = {
        "Low Cross-Sell Opportunity": 0.30,
        "Moderate Cross-Sell Opportunity": 0.65,
        "High Cross-Sell Opportunity": 1.00,
    }

    eligible["cross_sell_score"] = (
        eligible["cross_sell_opportunity"]
        .map(cross_sell_mapping)
        .fillna(0.50)
    )

    # ---------------------------------------------------------
    # Segment fit
    # ---------------------------------------------------------

    segment_scores = {
        "Premium High-Value": 1.00,
        "Core Active": 0.70,
        "At Risk": 0.45,
        "Dormant / Declining": 0.25,
    }

    eligible["segment_fit_score"] = (
        eligible["primary_segment"]
        .map(segment_scores)
        .fillna(0.50)
    )

    # ---------------------------------------------------------
    # Final recommendation score
    # ---------------------------------------------------------

    eligible["recommendation_score"] = (
        0.25 * eligible["product_fit_score"]
        + 0.20 * eligible["income_score"]
        + 0.15 * eligible["transaction_score"]
        + 0.10 * eligible["digital_score"]
        + 0.15 * eligible["segment_fit_score"]
        + 0.10 * eligible["historical_response_score"]
        + 0.05 * eligible["cross_sell_score"]
    )

    # ---------------------------------------------------------
    # Business adjustments
    # ---------------------------------------------------------

    # Positive spending trend
    eligible.loc[
        eligible["spending_trend"] > 0,
        "recommendation_score"
    ] += 0.02

    # Strong engagement
    eligible.loc[
        eligible["engagement_score"] >= 0.70,
        "recommendation_score"
    ] += 0.02

    # High-value customers
    eligible.loc[
        eligible["primary_segment"] == "Premium High-Value",
        "recommendation_score"
    ] += 0.03

    # Cap score
    eligible["recommendation_score"] = (
        eligible["recommendation_score"]
        .clip(0, 1)
    )

    # ---------------------------------------------------------
    # Recommendation confidence
    # ---------------------------------------------------------

    def confidence(score):

        if score >= 0.75:
            return "High"

        if score >= 0.55:
            return "Medium"

        return "Low"

    eligible["recommendation_confidence"] = (
        eligible["recommendation_score"]
        .apply(confidence)
    )

    # ---------------------------------------------------------
    # Ranking
    # ---------------------------------------------------------

    eligible["product_rank"] = (
        eligible
        .groupby("customer_id")["recommendation_score"]
        .rank(
            method="first",
            ascending=False
        )
        .astype(int)
    )

    # ---------------------------------------------------------
    # Final columns
    # ---------------------------------------------------------

    output_columns = [
        "customer_id",
        "product_id",
        "product_name",
        "product_type",
        "category",
        "already_owned",
        "eligible",

        "primary_segment",
        "customer_persona",
        "retention_risk",
        "cross_sell_opportunity",
        "genai_targeting_priority",

        "product_fit_score",
        "income_score",
        "balance_score",
        "spending_score",
        "transaction_score",
        "digital_score",
        "segment_fit_score",
        "historical_response_score",
        "cross_sell_score",

        "recommendation_score",
        "recommendation_confidence",
        "product_rank",
    ]

    output_columns = [
        c for c in output_columns
        if c in eligible.columns
    ]

    result = eligible[output_columns].copy()

    # Sort by customer and recommendation strength
    result = result.sort_values(
        ["customer_id", "recommendation_score"],
        ascending=[True, False]
    )

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print("SCORING VALIDATION")
    print("=" * 70)

    print(
        f"\nScored eligible pairs : {len(result):,}"
    )

    print(
        f"Unique customers      : "
        f"{result['customer_id'].nunique():,}"
    )

    print(
        f"Score minimum         : "
        f"{result['recommendation_score'].min():.4f}"
    )

    print(
        f"Score maximum         : "
        f"{result['recommendation_score'].max():.4f}"
    )

    print(
        f"Score average         : "
        f"{result['recommendation_score'].mean():.4f}"
    )

    print("\nConfidence distribution:")
    print(
        result["recommendation_confidence"]
        .value_counts()
        .to_string()
    )

    print("\nTop products by average score:")
    print(
        result
        .groupby("product_name")["recommendation_score"]
        .mean()
        .sort_values(ascending=False)
        .round(3)
        .to_string()
    )

    print("\nTop 10 recommendations:")
    print(
        result[
            [
                "customer_id",
                "product_name",
                "recommendation_score",
                "recommendation_confidence",
                "product_rank",
            ]
        ]
        .head(10)
        .to_string(index=False)
    )

    # ---------------------------------------------------------
    # Save
    # ---------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    result.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\n" + "=" * 70)
    print("PHASE 4B COMPLETE")
    print("=" * 70)

    print("\nSaved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()