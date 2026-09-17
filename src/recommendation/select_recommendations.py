from pathlib import Path
import pandas as pd
import numpy as np


INPUT_FILE = Path(
    "data/processed/customer_product_scores.csv"
)

OUTPUT_FILE = Path(
    "data/processed/customer_recommendations.csv"
)


# ============================================================
# PRODUCT-SPECIFIC REASON GENERATION
# ============================================================

def generate_reason(row):

    product = row["product_id"]

    reasons = []

    # Financial signals
    if row["income_score"] >= 0.70:
        reasons.append("strong income profile")

    if row["balance_score"] >= 0.70:
        reasons.append("strong account balance")

    # Transactional signals
    if row["transaction_score"] >= 0.70:
        reasons.append("high transaction activity")

    if row["spending_score"] >= 0.70:
        reasons.append("high spending activity")

    # Digital / engagement
    if row["digital_score"] >= 0.70:
        reasons.append("strong digital affinity")

    if row["segment_fit_score"] >= 0.80:
        reasons.append("strong segment fit")

    # Historical behavior
    if row["historical_response_score"] >= 0.60:
        reasons.append(
            "positive response to previous recommendations"
        )

    # Product-specific primary reasons
    product_reason = {
        "P003":
            "spending and transaction patterns support a rewards credit card",

        "P004":
            "financial capacity and transaction activity support borrowing needs",

        "P005":
            "financial capacity supports a potential home financing need",

        "P006":
            "financial capacity indicates potential for investment products",

        "P007":
            "customer profile indicates potential protection needs",

        "P008":
            "customer profile supports premium banking services",
    }

    primary = product_reason.get(
        product,
        "customer profile indicates product suitability"
    )

    if not reasons:
        reasons.append(primary)
    else:
        reasons.insert(0, primary)

    # Keep concise
    return "; ".join(reasons[:3])


# ============================================================
# PRODUCT-SPECIFIC BUSINESS PRIORITY
# ============================================================

def calculate_business_priority(row):

    product = row["product_id"]

    score = row["recommendation_score"]

    # --------------------------------------------------------
    # Product-specific adjustments
    # --------------------------------------------------------

    if product == "P003":

        # Credit card:
        # spending + digital behavior
        score += (
            0.04 * row["spending_score"]
            + 0.03 * row["digital_score"]
        )

    elif product == "P004":

        # Personal loan:
        # income + transaction activity
        score += (
            0.04 * row["income_score"]
            + 0.03 * row["transaction_score"]
        )

    elif product == "P005":

        # Home loan:
        # strong financial capacity
        score += (
            0.05 * row["income_score"]
            + 0.04 * row["balance_score"]
        )

    elif product == "P006":

        # Mutual fund:
        # balance + income
        score += (
            0.05 * row["balance_score"]
            + 0.04 * row["income_score"]
        )

    elif product == "P007":

        # Insurance:
        # income
        score += (
            0.04 * row["income_score"]
        )

    elif product == "P008":

        # Premium banking:
        # wealth + income
        score += (
            0.06 * row["balance_score"]
            + 0.04 * row["income_score"]
        )

    return min(score, 1.0)


# ============================================================
# CONFIDENCE
# ============================================================

def confidence(score):

    if score >= 0.75:
        return "High"

    elif score >= 0.55:
        return "Medium"

    else:
        return "Low"


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("PHASE 4C - TOP-N CUSTOMER RECOMMENDATION SELECTION")
    print("=" * 70)

    # --------------------------------------------------------
    # Load scoring data
    # --------------------------------------------------------

    print("\nLoading scored recommendations...")

    df = pd.read_csv(INPUT_FILE)

    print(
        f"Scored pairs : {len(df):,}"
    )

    print(
        f"Customers    : "
        f"{df['customer_id'].nunique():,}"
    )

    # --------------------------------------------------------
    # Business priority score
    # --------------------------------------------------------

    print(
        "\nApplying product-specific business adjustments..."
    )

    df["business_priority_score"] = df.apply(
        calculate_business_priority,
        axis=1
    )

    # ========================================================
    # IMPORTANT FIX
    # ========================================================
    #
    # The final recommendation score must be the SAME score
    # used for ranking.
    #
    # Previously:
    #
    # recommendation_score       -> original Phase 4B score
    # business_priority_score    -> adjusted score
    #
    # Ranking used business_priority_score, while Phase 4D
    # validated recommendation_score.
    #
    # This caused score-order violations.
    #
    # Now:
    #
    # recommendation_score
    #          =
    # business_priority_score
    #
    # Therefore ranking and validation use the same score.
    # ========================================================

    df["recommendation_score"] = (
        df["business_priority_score"]
    )

    # --------------------------------------------------------
    # Final ranking
    # --------------------------------------------------------

    df = df.sort_values(
        [
            "customer_id",
            "recommendation_score",
            "product_id",
        ],
        ascending=[
            True,
            False,
            True,
        ],
    ).copy()

    # Rank within each customer
    df["recommendation_rank"] = (
        df.groupby("customer_id")
        .cumcount()
        + 1
    )

    # --------------------------------------------------------
    # Recommendation strength
    # --------------------------------------------------------

    df["recommendation_confidence"] = (
        df["recommendation_score"]
        .apply(confidence)
    )

    # --------------------------------------------------------
    # Recommendation reason
    # --------------------------------------------------------

    print(
        "Generating recommendation reasons..."
    )

    df["recommendation_reason"] = df.apply(
        generate_reason,
        axis=1
    )

    # --------------------------------------------------------
    # Select Top 3
    # --------------------------------------------------------

    top3 = df[
        df["recommendation_rank"] <= 3
    ].copy()

    # --------------------------------------------------------
    # Recommendation priority
    # --------------------------------------------------------

    def priority(rank):

        if rank == 1:
            return "Primary Recommendation"

        elif rank == 2:
            return "Secondary Recommendation"

        return "Alternative Recommendation"

    top3["recommendation_priority"] = (
        top3["recommendation_rank"]
        .apply(priority)
    )

    # --------------------------------------------------------
    # Score gap to next recommendation
    # --------------------------------------------------------

    # Since df is already sorted by final recommendation
    # score, calculate the difference between consecutive
    # recommendations for each customer.

    top3["score_gap_to_next"] = (
        top3.groupby("customer_id")["recommendation_score"]
        .shift(-1)
    )

    top3["score_gap_to_next"] = (
        top3["recommendation_score"]
        - top3["score_gap_to_next"]
    )

    # Last recommendation has no next recommendation
    top3["score_gap_to_next"] = (
        top3["score_gap_to_next"]
        .fillna(0.0)
        .clip(lower=0)
    )

    # --------------------------------------------------------
    # Final columns
    # --------------------------------------------------------

    columns = [
        "customer_id",

        "product_id",
        "product_name",
        "product_type",
        "category",

        "primary_segment",
        "customer_persona",
        "retention_risk",
        "cross_sell_opportunity",
        "genai_targeting_priority",

        "recommendation_rank",
        "recommendation_priority",

        "recommendation_score",
        "business_priority_score",
        "recommendation_confidence",

        "score_gap_to_next",
        "recommendation_reason",

        # Supporting signals
        "income_score",
        "balance_score",
        "spending_score",
        "transaction_score",
        "digital_score",
        "segment_fit_score",
        "historical_response_score",
        "cross_sell_score",
    ]

    columns = [
        c for c in columns
        if c in top3.columns
    ]

    result = top3[columns].copy()

    # --------------------------------------------------------
    # Final sort
    # --------------------------------------------------------

    result = result.sort_values(
        [
            "customer_id",
            "recommendation_rank",
        ]
    ).reset_index(drop=True)

    # ========================================================
    # VALIDATION
    # ========================================================

    print(
        "\n" + "=" * 70
    )

    print(
        "TOP-N RECOMMENDATION VALIDATION"
    )

    print(
        "=" * 70
    )

    customers = result[
        "customer_id"
    ].nunique()

    print(
        f"\nCustomers with recommendations : "
        f"{customers:,}"
    )

    print(
        f"Recommendation rows             : "
        f"{len(result):,}"
    )

    print(
        f"Average recommendations/customer: "
        f"{len(result) / customers:.2f}"
    )

    print(
        "\nRecommendation rank distribution:"
    )

    print(
        result[
            "recommendation_rank"
        ]
        .value_counts()
        .sort_index()
        .to_string()
    )

    print(
        "\nConfidence distribution:"
    )

    print(
        result[
            "recommendation_confidence"
        ]
        .value_counts()
        .to_string()
    )

    print(
        "\nProduct recommendation distribution:"
    )

    print(
        result[
            "product_name"
        ]
        .value_counts()
        .to_string()
    )

    print(
        "\nPrimary recommendations:"
    )

    print(
        result[
            result["recommendation_rank"] == 1
        ]["product_name"]
        .value_counts()
        .to_string()
    )

    # --------------------------------------------------------
    # Verify score ordering before saving
    # --------------------------------------------------------

    violations = 0

    for customer_id, group in result.groupby(
        "customer_id"
    ):

        scores = group[
            "recommendation_score"
        ].tolist()

        if scores != sorted(
            scores,
            reverse=True
        ):
            violations += 1

    print(
        "\nScore ordering validation:"
    )

    print(
        f"Customers violating score ordering : "
        f"{violations}"
    )

    if violations == 0:

        print(
            "PASS - Recommendation ranks follow "
            "final recommendation scores"
        )

    else:

        print(
            "WARNING - Score ordering violations detected"
        )

    # --------------------------------------------------------
    # Show sample customers
    # --------------------------------------------------------

    print(
        "\n" + "=" * 70
    )

    print(
        "SAMPLE TOP-3 RECOMMENDATIONS"
    )

    print(
        "=" * 70
    )

    sample_customers = (
        result[
            "customer_id"
        ]
        .drop_duplicates()
        .head(5)
    )

    for customer_id in sample_customers:

        customer = result[
            result["customer_id"] == customer_id
        ]

        print(
            f"\nCustomer: {customer_id}"
        )

        for _, row in customer.iterrows():

            print(
                f"  "
                f"{int(row['recommendation_rank'])}. "
                f"{row['product_name']} | "
                f"Score: "
                f"{row['recommendation_score']:.3f} | "
                f"{row['recommendation_confidence']}"
            )

            print(
                f"     Reason: "
                f"{row['recommendation_reason']}"
            )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    result.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "PHASE 4C COMPLETE"
    )

    print(
        "=" * 70
    )

    print(
        "\nSaved to:"
    )

    print(
        OUTPUT_FILE
    )

    print(
        f"\nRows    : "
        f"{len(result):,}"
    )

    print(
        f"Columns : "
        f"{len(result.columns):,}"
    )


if __name__ == "__main__":
    main()