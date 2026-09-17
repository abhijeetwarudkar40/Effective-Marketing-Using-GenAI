import pandas as pd
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

PROCESSED_DIR = BASE_DIR / "data" / "processed"

AB_FILE = PROCESSED_DIR / "campaign_ab_variants.csv"
RECOMMENDATION_FILE = (
    PROCESSED_DIR / "customer_recommendations.csv"
)

OUTPUT_FILE = (
    PROCESSED_DIR / "campaign_analytics.csv"
)

SUMMARY_FILE = (
    PROCESSED_DIR / "campaign_ab_summary.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

def load_data():
    """
    Load Phase 5D A/B campaign variants and
    recommendation data.
    """

    if not AB_FILE.exists():
        raise FileNotFoundError(
            f"A/B campaign file not found:\n{AB_FILE}"
        )

    if not RECOMMENDATION_FILE.exists():
        raise FileNotFoundError(
            "Recommendation file not found:\n"
            f"{RECOMMENDATION_FILE}"
        )

    ab = pd.read_csv(AB_FILE)

    recommendations = pd.read_csv(
        RECOMMENDATION_FILE
    )

    return ab, recommendations


# ============================================================
# BUILD ANALYTICS
# ============================================================

def build_analytics(ab, recommendations):
    """
    Build campaign analytics and A/B evaluation
    from the wide-format campaign_ab_variants.csv.

    Phase 5D format:

        variant_a_strategy
        variant_a_subject
        variant_a_headline
        variant_a_body
        variant_a_cta

        variant_b_strategy
        variant_b_subject
        variant_b_headline
        variant_b_body
        variant_b_cta

    No single "variant" column is required.
    """

    analytics = ab.copy()

    # --------------------------------------------------------
    # BASIC NUMERIC METRICS
    # --------------------------------------------------------

    if "recommendation_score" in analytics.columns:

        analytics["recommendation_score"] = pd.to_numeric(
            analytics["recommendation_score"],
            errors="coerce"
        ).fillna(0)

    else:

        analytics["recommendation_score"] = 0.0

    if "recommendation_confidence" in analytics.columns:

        analytics["recommendation_confidence"] = pd.to_numeric(
            analytics["recommendation_confidence"],
            errors="coerce"
        ).fillna(0)

    else:

        analytics["recommendation_confidence"] = 0.0

    # --------------------------------------------------------
    # TEST GROUP
    # --------------------------------------------------------

    analytics["test_group"] = "A/B"

    # --------------------------------------------------------
    # VARIANT STRATEGIES
    # --------------------------------------------------------

    if "variant_a_strategy" in analytics.columns:

        analytics["variant_a"] = (
            analytics["variant_a_strategy"]
        )

    else:

        analytics["variant_a"] = "Benefit-Focused"

    if "variant_b_strategy" in analytics.columns:

        analytics["variant_b"] = (
            analytics["variant_b_strategy"]
        )

    else:

        analytics["variant_b"] = "Action-Focused"

    # --------------------------------------------------------
    # ESTIMATED PERFORMANCE SCORES
    # --------------------------------------------------------
    #
    # IMPORTANT:
    # These are MODEL-BASED analytical scores.
    #
    # They are NOT actual:
    #   - email opens
    #   - clicks
    #   - conversions
    #   - purchases
    #
    # Real A/B testing requires campaign response data.
    # --------------------------------------------------------

    analytics["variant_a_score"] = (
        analytics["recommendation_score"] * 0.60
        +
        analytics["recommendation_confidence"] * 0.40
    )

    analytics["variant_b_score"] = (
        analytics["recommendation_score"] * 0.55
        +
        analytics["recommendation_confidence"] * 0.45
    )

    # --------------------------------------------------------
    # OBJECTIVE ADJUSTMENTS
    # --------------------------------------------------------

    if "campaign_objective" in analytics.columns:

        analytics.loc[
            analytics["campaign_objective"] == "Retention",
            "variant_a_score"
        ] += 2

        analytics.loc[
            analytics["campaign_objective"] == "Engagement",
            "variant_b_score"
        ] += 2

        analytics.loc[
            analytics["campaign_objective"] == "Cross-Sell",
            "variant_a_score"
        ] += 1

        analytics.loc[
            analytics["campaign_objective"] == "Upsell",
            "variant_b_score"
        ] += 1

    # --------------------------------------------------------
    # NORMALIZE SCORES
    # --------------------------------------------------------

    max_score = max(
        analytics["variant_a_score"].max(),
        analytics["variant_b_score"].max(),
        1
    )

    analytics["variant_a_score"] = (
        analytics["variant_a_score"]
        / max_score
        * 100
    )

    analytics["variant_b_score"] = (
        analytics["variant_b_score"]
        / max_score
        * 100
    )

    # --------------------------------------------------------
    # WINNING VARIANT
    # --------------------------------------------------------

    analytics["winning_variant"] = analytics.apply(
        lambda row:
            "A"
            if row["variant_a_score"]
            > row["variant_b_score"]
            else
            "B"
            if row["variant_b_score"]
            > row["variant_a_score"]
            else
            "Tie",
        axis=1
    )

    # --------------------------------------------------------
    # WINNING STRATEGY
    # --------------------------------------------------------

    analytics["winning_strategy"] = (
        analytics["winning_variant"]
        .map(
            {
                "A": "Benefit-Focused",
                "B": "Action-Focused",
                "Tie": "Equal",
            }
        )
    )

    # --------------------------------------------------------
    # SCORE DIFFERENCE
    # --------------------------------------------------------

    analytics["score_difference"] = (
        analytics["variant_a_score"]
        -
        analytics["variant_b_score"]
    ).abs()

    # --------------------------------------------------------
    # A/B CONFIDENCE
    # --------------------------------------------------------

    analytics["ab_confidence"] = (
        analytics["score_difference"]
        .apply(
            lambda x:
                "High"
                if x >= 15
                else
                "Medium"
                if x >= 5
                else
                "Low"
        )
    )

    # --------------------------------------------------------
    # RECOMMENDATION COUNT
    # --------------------------------------------------------

    analytics["recommendation_count"] = 0

    if (
        recommendations is not None
        and not recommendations.empty
        and "customer_id" in recommendations.columns
        and "customer_id" in analytics.columns
    ):

        rec_summary = (
            recommendations
            .groupby("customer_id")
            .size()
            .reset_index(
                name="recommendation_count"
            )
        )

        analytics = analytics.merge(
            rec_summary,
            on="customer_id",
            how="left",
            suffixes=("", "_from_recommendations")
        )

        if (
            "recommendation_count_from_recommendations"
            in analytics.columns
        ):

            analytics["recommendation_count"] = (
                analytics[
                    "recommendation_count_from_recommendations"
                ]
            )

            analytics.drop(
                columns=[
                    "recommendation_count_from_recommendations"
                ],
                inplace=True
            )

    analytics["recommendation_count"] = (
        pd.to_numeric(
            analytics["recommendation_count"],
            errors="coerce"
        )
        .fillna(0)
        .astype(int)
    )

    # --------------------------------------------------------
    # EVALUATION TYPE
    # --------------------------------------------------------

    analytics["evaluation_type"] = (
        "Model-Based A/B Evaluation"
    )

    # --------------------------------------------------------
    # ANALYTICS NOTE
    # --------------------------------------------------------

    analytics["analytics_note"] = (
        "Estimated model-based performance; "
        "not based on actual customer engagement data."
    )

    return analytics


# ============================================================
# VALIDATION
# ============================================================

def validate_analytics(df):
    """
    Validate campaign analytics.
    """

    print()
    print("=" * 70)
    print("CAMPAIGN ANALYTICS VALIDATION")
    print("=" * 70)

    print()
    print(
        f"Analytics rows       : {len(df):,}"
    )

    if "customer_id" in df.columns:

        print(
            f"Unique customers     : "
            f"{df['customer_id'].nunique():,}"
        )

        duplicate_customers = (
            df["customer_id"]
            .duplicated()
            .sum()
        )

    else:

        duplicate_customers = len(df)

        print(
            "Unique customers     : 0"
        )

    print(
        f"Duplicate customers  : "
        f"{duplicate_customers:,}"
    )

    # --------------------------------------------------------
    # REQUIRED A/B COLUMNS
    # --------------------------------------------------------

    required_ab_columns = [

        "variant_a_strategy",
        "variant_a_subject",
        "variant_a_headline",
        "variant_a_body",
        "variant_a_cta",

        "variant_b_strategy",
        "variant_b_subject",
        "variant_b_headline",
        "variant_b_body",
        "variant_b_cta",
    ]

    missing_columns = [
        column
        for column in required_ab_columns
        if column not in df.columns
    ]

    if missing_columns:

        print()
        print("Missing A/B columns:")

        for column in missing_columns:

            print(
                f"  - {column}"
            )

    # --------------------------------------------------------
    # MISSING CONTENT
    # --------------------------------------------------------

    missing_content = 0

    for column in required_ab_columns:

        if column not in df.columns:
            continue

        missing_content += (
            df[column]
            .isna()
            .sum()
        )

        missing_content += (
            df[column]
            .astype(str)
            .str.strip()
            .eq("")
            .sum()
        )

    print(
        f"Missing A/B content  : "
        f"{missing_content:,}"
    )

    # --------------------------------------------------------
    # IDENTICAL VARIANTS
    # --------------------------------------------------------

    identical_variants = 0

    if (
        "variant_a_subject" in df.columns
        and
        "variant_b_subject" in df.columns
        and
        "variant_a_body" in df.columns
        and
        "variant_b_body" in df.columns
    ):

        identical_variants = (
            (
                df["variant_a_subject"]
                .astype(str)
                .str.strip()
                ==
                df["variant_b_subject"]
                .astype(str)
                .str.strip()
            )
            &
            (
                df["variant_a_body"]
                .astype(str)
                .str.strip()
                ==
                df["variant_b_body"]
                .astype(str)
                .str.strip()
            )
        ).sum()

    print(
        f"Identical A/B variants : "
        f"{identical_variants:,}"
    )

    # --------------------------------------------------------
    # WINNER DISTRIBUTION
    # --------------------------------------------------------

    if "winning_variant" in df.columns:

        print()
        print("Winning Variant Distribution")
        print("-" * 70)

        print(
            df["winning_variant"]
            .value_counts()
        )

    # --------------------------------------------------------
    # STRATEGY DISTRIBUTION
    # --------------------------------------------------------

    if "winning_strategy" in df.columns:

        print()
        print("Winning Strategy Distribution")
        print("-" * 70)

        print(
            df["winning_strategy"]
            .value_counts()
        )

    # --------------------------------------------------------
    # CONFIDENCE DISTRIBUTION
    # --------------------------------------------------------

    if "ab_confidence" in df.columns:

        print()
        print("A/B Confidence Distribution")
        print("-" * 70)

        print(
            df["ab_confidence"]
            .value_counts()
        )

    # --------------------------------------------------------
    # OBJECTIVE DISTRIBUTION
    # --------------------------------------------------------

    if "campaign_objective" in df.columns:

        print()
        print("Campaign Objective Distribution")
        print("-" * 70)

        print(
            df["campaign_objective"]
            .value_counts()
        )

    # --------------------------------------------------------
    # VALIDATION RESULT
    # --------------------------------------------------------

    validation_pass = (
        duplicate_customers == 0
        and missing_content == 0
        and identical_variants == 0
        and len(missing_columns) == 0
    )

    print()

    if validation_pass:

        print(
            "PASS - Campaign analytics validation successful"
        )

    else:

        print(
            "WARNING - Campaign analytics validation "
            "found issues"
        )

    return validation_pass


# ============================================================
# A/B SUMMARY
# ============================================================

def generate_ab_summary(df):
    """
    Generate a DataFrame containing the overall A/B summary.

    IMPORTANT:
    This function returns a pandas DataFrame so that the
    result can safely be printed using to_string() and
    saved using to_csv().
    """

    print()
    print("=" * 70)
    print("A/B PERFORMANCE SUMMARY")
    print("=" * 70)

    total_campaigns = len(df)

    # --------------------------------------------------------
    # VARIANT A
    # --------------------------------------------------------

    variant_a_avg_score = (
        df["variant_a_score"].mean()
        if "variant_a_score" in df.columns
        else 0
    )

    variant_a_wins = (
        (
            df["winning_variant"]
            == "A"
        ).sum()
        if "winning_variant" in df.columns
        else 0
    )

    variant_a_win_rate = (
        variant_a_wins
        /
        total_campaigns
        *
        100
        if total_campaigns > 0
        else 0
    )

    # --------------------------------------------------------
    # VARIANT B
    # --------------------------------------------------------

    variant_b_avg_score = (
        df["variant_b_score"].mean()
        if "variant_b_score" in df.columns
        else 0
    )

    variant_b_wins = (
        (
            df["winning_variant"]
            == "B"
        ).sum()
        if "winning_variant" in df.columns
        else 0
    )

    variant_b_win_rate = (
        variant_b_wins
        /
        total_campaigns
        *
        100
        if total_campaigns > 0
        else 0
    )

    # --------------------------------------------------------
    # TIES
    # --------------------------------------------------------

    tie_count = (
        (
            df["winning_variant"]
            == "Tie"
        ).sum()
        if "winning_variant" in df.columns
        else 0
    )

    tie_rate = (
        tie_count
        /
        total_campaigns
        *
        100
        if total_campaigns > 0
        else 0
    )

    # --------------------------------------------------------
    # OVERALL WINNER
    # --------------------------------------------------------

    if variant_a_wins > variant_b_wins:

        overall_winner = "A"
        overall_strategy = "Benefit-Focused"

    elif variant_b_wins > variant_a_wins:

        overall_winner = "B"
        overall_strategy = "Action-Focused"

    else:

        overall_winner = "Tie"
        overall_strategy = "Equal"

    # --------------------------------------------------------
    # PRINT OVERALL SUMMARY
    # --------------------------------------------------------

    print()
    print("Variant A")
    print("-" * 70)

    print(
        "Strategy        : Benefit-Focused"
    )

    print(
        f"Campaigns       : "
        f"{total_campaigns:,}"
    )

    print(
        f"Average Score   : "
        f"{variant_a_avg_score:.2f}"
    )

    print(
        f"Wins            : "
        f"{variant_a_wins:,}"
    )

    print(
        f"Win Rate        : "
        f"{variant_a_win_rate:.2f}%"
    )

    print()
    print("Variant B")
    print("-" * 70)

    print(
        "Strategy        : Action-Focused"
    )

    print(
        f"Campaigns       : "
        f"{total_campaigns:,}"
    )

    print(
        f"Average Score   : "
        f"{variant_b_avg_score:.2f}"
    )

    print(
        f"Wins            : "
        f"{variant_b_wins:,}"
    )

    print(
        f"Win Rate        : "
        f"{variant_b_win_rate:.2f}%"
    )

    print()
    print("Ties")
    print("-" * 70)

    print(
        f"Campaigns       : "
        f"{tie_count:,}"
    )

    print(
        f"Rate            : "
        f"{tie_rate:.2f}%"
    )

    print()
    print("Overall Winner")
    print("-" * 70)

    print(
        f"Winning Variant  : "
        f"{overall_winner}"
    )

    print(
        f"Winning Strategy : "
        f"{overall_strategy}"
    )

    # --------------------------------------------------------
    # SUMMARY DATAFRAME
    # --------------------------------------------------------

    summary_rows = [

        {
            "summary_type": "Overall",
            "category": "Variant A",
            "strategy": "Benefit-Focused",
            "campaign_count": total_campaigns,
            "average_score": round(
                float(variant_a_avg_score),
                2
            ),
            "wins": int(variant_a_wins),
            "win_rate_percent": round(
                float(variant_a_win_rate),
                2
            ),
        },

        {
            "summary_type": "Overall",
            "category": "Variant B",
            "strategy": "Action-Focused",
            "campaign_count": total_campaigns,
            "average_score": round(
                float(variant_b_avg_score),
                2
            ),
            "wins": int(variant_b_wins),
            "win_rate_percent": round(
                float(variant_b_win_rate),
                2
            ),
        },

        {
            "summary_type": "Overall",
            "category": "Tie",
            "strategy": "Equal",
            "campaign_count": total_campaigns,
            "average_score": None,
            "wins": int(tie_count),
            "win_rate_percent": round(
                float(tie_rate),
                2
            ),
        },

        {
            "summary_type": "Overall Winner",
            "category": overall_winner,
            "strategy": overall_strategy,
            "campaign_count": total_campaigns,
            "average_score": None,
            "wins": max(
                variant_a_wins,
                variant_b_wins,
            ),
            "win_rate_percent": round(
                max(
                    variant_a_win_rate,
                    variant_b_win_rate,
                ),
                2
            ),
        },
    ]

    # --------------------------------------------------------
    # OBJECTIVE-LEVEL ANALYSIS
    # --------------------------------------------------------

    if (
        "campaign_objective" in df.columns
        and
        "winning_variant" in df.columns
    ):

        objective_summary = (
            df.groupby(
                [
                    "campaign_objective",
                    "winning_variant",
                ]
            )
            .size()
            .reset_index(
                name="campaign_count"
            )
        )

        print()
        print("Winner by Campaign Objective")
        print("-" * 70)

        print(
            objective_summary.to_string(
                index=False
            )
        )

        for _, row in objective_summary.iterrows():

            strategy = {
                "A": "Benefit-Focused",
                "B": "Action-Focused",
                "Tie": "Equal",
            }.get(
                row["winning_variant"],
                "Unknown"
            )

            summary_rows.append(
                {
                    "summary_type": "Objective",
                    "category": row[
                        "campaign_objective"
                    ],
                    "strategy": strategy,
                    "campaign_count": int(
                        row["campaign_count"]
                    ),
                    "average_score": None,
                    "wins": int(
                        row["campaign_count"]
                    ),
                    "win_rate_percent": None,
                }
            )

    # --------------------------------------------------------
    # PRODUCT-LEVEL ANALYSIS
    # --------------------------------------------------------

    if (
        "product_name" in df.columns
        and
        "winning_variant" in df.columns
    ):

        product_summary = (
            df.groupby(
                [
                    "product_name",
                    "winning_variant",
                ]
            )
            .size()
            .reset_index(
                name="campaign_count"
            )
        )

        print()
        print("Winner by Product")
        print("-" * 70)

        print(
            product_summary.to_string(
                index=False
            )
        )

        for _, row in product_summary.iterrows():

            strategy = {
                "A": "Benefit-Focused",
                "B": "Action-Focused",
                "Tie": "Equal",
            }.get(
                row["winning_variant"],
                "Unknown"
            )

            summary_rows.append(
                {
                    "summary_type": "Product",
                    "category": row[
                        "product_name"
                    ],
                    "strategy": strategy,
                    "campaign_count": int(
                        row["campaign_count"]
                    ),
                    "average_score": None,
                    "wins": int(
                        row["campaign_count"]
                    ),
                    "win_rate_percent": None,
                }
            )

    # --------------------------------------------------------
    # RETURN DATAFRAME
    # --------------------------------------------------------

    return pd.DataFrame(
        summary_rows
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("PHASE 5E - CAMPAIGN ANALYTICS & A/B EVALUATION")
    print("=" * 70)

    print()

    # --------------------------------------------------------
    # LOAD DATA
    # --------------------------------------------------------

    ab, recommendations = load_data()

    print(
        f"A/B variants loaded       : "
        f"{len(ab):,}"
    )

    print(
        f"Recommendations loaded    : "
        f"{len(recommendations):,}"
    )

    print()

    # --------------------------------------------------------
    # BUILD ANALYTICS
    # --------------------------------------------------------

    print(
        "Building campaign analytics..."
    )

    analytics = build_analytics(
        ab,
        recommendations
    )

    # --------------------------------------------------------
    # VALIDATE
    # --------------------------------------------------------

    validation_pass = validate_analytics(
        analytics
    )

    # --------------------------------------------------------
    # A/B SUMMARY
    # --------------------------------------------------------

    summary = generate_ab_summary(
        analytics
    )

    # --------------------------------------------------------
    # FINAL SUMMARY
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("FINAL A/B SUMMARY")
    print("=" * 70)

    print()

    print(
        summary.to_string(
            index=False
        )
    )

    # --------------------------------------------------------
    # SAVE ANALYTICS
    # --------------------------------------------------------

    analytics.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # --------------------------------------------------------
    # SAVE SUMMARY
    # --------------------------------------------------------

    summary.to_csv(
        SUMMARY_FILE,
        index=False
    )

    # --------------------------------------------------------
    # FINAL STATUS
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("PHASE 5E COMPLETE")
    print("=" * 70)

    print()

    print(
        "Validation Status : "
        + (
            "PASS"
            if validation_pass
            else "WARNING"
        )
    )

    print()

    print(
        "Analytics saved to:"
    )

    print(
        OUTPUT_FILE
    )

    print()

    print(
        "A/B summary saved to:"
    )

    print(
        SUMMARY_FILE
    )

    print()

    print(
        f"Analytics rows : "
        f"{len(analytics):,}"
    )

    print(
        f"Analytics columns : "
        f"{len(analytics.columns):,}"
    )

    print(
        f"Summary rows : "
        f"{len(summary):,}"
    )

    print()

    print(
        "NOTE:"
    )

    print(
        "A/B performance is currently "
        "model-based because actual "
        "customer engagement data "
        "(opens, clicks, conversions) "
        "is not available."
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()