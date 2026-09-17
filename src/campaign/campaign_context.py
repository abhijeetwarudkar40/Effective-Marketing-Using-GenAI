import pandas as pd
from pathlib import Path


# ============================================================
# PHASE 5B - CAMPAIGN CONTEXT
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

PROCESSED_DIR = BASE_DIR / "data" / "processed"


SEGMENTS_FILE = PROCESSED_DIR / "customer_segments.csv"
RECOMMENDATIONS_FILE = PROCESSED_DIR / "customer_recommendations.csv"

OUTPUT_FILE = PROCESSED_DIR / "campaign_context.csv"


# ============================================================
# LOAD DATA
# ============================================================

def load_data():

    segments = pd.read_csv(SEGMENTS_FILE)

    recommendations = pd.read_csv(
        RECOMMENDATIONS_FILE
    )

    return segments, recommendations


# ============================================================
# CAMPAIGN OBJECTIVE
# ============================================================

def determine_campaign_objective(row):

    segment = str(
        row.get("primary_segment", "")
    )

    persona = str(
        row.get("customer_persona", "")
    )

    risk = str(
        row.get("retention_risk", "")
    )

    cross_sell = str(
        row.get("cross_sell_opportunity", "")
    )

    product = str(
        row.get("product_name", "")
    )

    # ----------------------------------------
    # RETENTION
    # ----------------------------------------

    if risk in [
        "Critical Risk",
        "High Risk"
    ]:

        return "Retention"

    # ----------------------------------------
    # REACTIVATION
    # ----------------------------------------

    if segment == "Dormant / Declining":

        return "Reactivation"

    if "Dormant" in persona:

        return "Reactivation"

    # ----------------------------------------
    # CROSS SELL
    # ----------------------------------------

    if cross_sell in [
        "High Cross-Sell Opportunity",
        "Moderate Cross-Sell Opportunity"
    ]:

        return "Cross-Sell"

    if "Cross-Sell" in persona:

        return "Cross-Sell"

    # ----------------------------------------
    # PREMIUM / UPSELL
    # ----------------------------------------

    if segment == "Premium High-Value":

        return "Upsell"

    if "Premium" in persona:

        return "Upsell"

    # ----------------------------------------
    # DEFAULT
    # ----------------------------------------

    return "Engagement"


# ============================================================
# MARKETING ANGLE
# ============================================================

def determine_marketing_angle(row):

    product = str(
        row.get("product_name", "")
    )

    objective = str(
        row.get("campaign_objective", "")
    )

    digital_score = row.get(
        "digital_usage_score",
        0
    )

    spending_trend = str(
        row.get("spending_trend", "")
    )

    # ----------------------------------------
    # PRODUCT BASED ANGLES
    # ----------------------------------------

    product_angles = {

        "Rewards Credit Card":
            "Highlight rewards, benefits and spending value",

        "Personal Loan":
            "Highlight flexible financing and convenience",

        "Home Loan":
            "Highlight long-term home financing value",

        "Mutual Fund Plan":
            "Highlight wealth creation and investment potential",

        "Term Insurance":
            "Highlight financial protection and security",

        "Premium Banking":
            "Highlight premium services and exclusive benefits",
    }

    angle = product_angles.get(
        product,
        "Highlight relevant product benefits"
    )

    # ----------------------------------------
    # OBJECTIVE MODIFIER
    # ----------------------------------------

    if objective == "Retention":

        angle = (
            "Strengthen the customer relationship while "
            + angle.lower()
        )

    elif objective == "Reactivation":

        angle = (
            "Re-engage the customer with a relevant offer "
            "and " + angle.lower()
        )

    elif objective == "Upsell":

        angle = (
            "Emphasize premium value and " +
            angle.lower()
        )

    elif objective == "Cross-Sell":

        angle = (
            "Introduce a complementary product and " +
            angle.lower()
        )

    # ----------------------------------------
    # DIGITAL MODIFIER
    # ----------------------------------------

    try:

        if float(digital_score) >= 0.70:

            angle += "; prioritize digital engagement"

    except:

        pass

    # ----------------------------------------
    # SPENDING MODIFIER
    # ----------------------------------------

    if spending_trend.lower() in [
        "increasing",
        "growing",
        "upward"
    ]:

        angle += "; leverage recent spending activity"

    return angle


# ============================================================
# CUSTOMER CONTEXT
# ============================================================

def build_campaign_context(
    segments,
    recommendations
):

    print("Building campaign context...")

    # --------------------------------------------------------
    # Select primary recommendation per customer
    # --------------------------------------------------------

    recommendations = recommendations.copy()

    if "recommendation_rank" in recommendations.columns:

        recommendations = recommendations.sort_values(
            [
                "customer_id",
                "recommendation_rank"
            ]
        )

        recommendations = (
            recommendations
            .groupby(
                "customer_id",
                as_index=False
            )
            .first()
        )

    # --------------------------------------------------------
    # Merge segmentation + recommendation
    # --------------------------------------------------------

    context = segments.merge(
        recommendations,
        on="customer_id",
        how="inner",
        suffixes=("", "_recommendation")
    )

    # --------------------------------------------------------
    # Campaign objective
    # --------------------------------------------------------

    context["campaign_objective"] = context.apply(
        determine_campaign_objective,
        axis=1
    )

    # --------------------------------------------------------
    # Marketing angle
    # --------------------------------------------------------

    context["marketing_angle"] = context.apply(
        determine_marketing_angle,
        axis=1
    )

    # --------------------------------------------------------
    # Campaign priority
    # --------------------------------------------------------

    if "genai_targeting_priority" in context.columns:

        context["campaign_priority"] = (
            context["genai_targeting_priority"]
        )

    else:

        context["campaign_priority"] = "Standard"

    # --------------------------------------------------------
    # Recommendation strength
    # --------------------------------------------------------

    if "recommendation_score" in context.columns:

        context["recommendation_strength"] = (
            context["recommendation_score"]
        )

    else:

        context["recommendation_strength"] = 0.0

    # --------------------------------------------------------
    # Context readiness
    # --------------------------------------------------------

    context["campaign_context_ready"] = True

    return context


# ============================================================
# SELECT OUTPUT COLUMNS
# ============================================================

def select_output_columns(context):

    preferred_columns = [

        # Customer
        "customer_id",

        # Segmentation
        "primary_segment",
        "customer_persona",

        # Risk / opportunity
        "retention_risk",
        "cross_sell_opportunity",
        "genai_targeting_priority",

        # Financial profile
        "annual_income",
        "average_account_balance",
        "monthly_spending",

        # Behavior
        "transaction_count",
        "recency_days",
        "digital_usage_score",
        "products_held",
        "engagement_score",

        # Recommendation
        "product_id",
        "product_name",
        "recommendation_score",
        "recommendation_confidence",
        "recommendation_reason",

        # Campaign
        "campaign_objective",
        "marketing_angle",
        "campaign_priority",
        "recommendation_strength",

        # Status
        "campaign_context_ready",
    ]

    available_columns = [
        col
        for col in preferred_columns
        if col in context.columns
    ]

    return context[available_columns]


# ============================================================
# VALIDATION
# ============================================================

def validate_context(context):

    print()
    print("=" * 70)
    print("CAMPAIGN CONTEXT VALIDATION")
    print("=" * 70)

    print()

    print(
        f"Campaign contexts : {len(context):,}"
    )

    print(
        f"Unique customers  : "
        f"{context['customer_id'].nunique():,}"
    )

    # --------------------------------------------------------
    # Duplicate customers
    # --------------------------------------------------------

    duplicate_customers = (
        context["customer_id"]
        .duplicated()
        .sum()
    )

    print(
        f"Duplicate customers : "
        f"{duplicate_customers}"
    )

    # --------------------------------------------------------
    # Missing products
    # --------------------------------------------------------

    if "product_name" in context.columns:

        missing_products = (
            context["product_name"]
            .isna()
            .sum()
        )

        print(
            f"Missing products : "
            f"{missing_products}"
        )

    # --------------------------------------------------------
    # Objective distribution
    # --------------------------------------------------------

    if "campaign_objective" in context.columns:

        print()
        print("Campaign Objective Distribution")
        print("-" * 70)

        print(
            context[
                "campaign_objective"
            ].value_counts()
        )

    # --------------------------------------------------------
    # Product distribution
    # --------------------------------------------------------

    if "product_name" in context.columns:

        print()
        print("Primary Campaign Product Distribution")
        print("-" * 70)

        print(
            context[
                "product_name"
            ].value_counts()
        )

    # --------------------------------------------------------
    # Readiness
    # --------------------------------------------------------

    ready = (
        context["campaign_context_ready"]
        .eq(True)
        .sum()
    )

    print()
    print(
        f"Campaign contexts ready : "
        f"{ready:,}"
    )

    print()

    if (
        duplicate_customers == 0
        and ready == len(context)
    ):

        print(
            "PASS - Campaign context validation successful"
        )

    else:

        print(
            "WARNING - Review campaign context validation"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("PHASE 5B - CAMPAIGN CONTEXT")
    print("=" * 70)

    print()

    # --------------------------------------------------------
    # Check files
    # --------------------------------------------------------

    if not SEGMENTS_FILE.exists():

        raise FileNotFoundError(
            f"Missing file: {SEGMENTS_FILE}"
        )

    if not RECOMMENDATIONS_FILE.exists():

        raise FileNotFoundError(
            f"Missing file: {RECOMMENDATIONS_FILE}"
        )

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    segments, recommendations = load_data()

    print(
        f"Customers loaded       : "
        f"{segments['customer_id'].nunique():,}"
    )

    print(
        f"Recommendations loaded : "
        f"{len(recommendations):,}"
    )

    # --------------------------------------------------------
    # Build context
    # --------------------------------------------------------

    context = build_campaign_context(
        segments,
        recommendations
    )

    # --------------------------------------------------------
    # Select columns
    # --------------------------------------------------------

    context = select_output_columns(
        context
    )

    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    validate_context(context)

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    context.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print()
    print("=" * 70)
    print("PHASE 5B COMPLETE")
    print("=" * 70)

    print()

    print("Saved to:")
    print(OUTPUT_FILE)

    print()

    print(
        f"Rows    : {len(context):,}"
    )

    print(
        f"Columns : {len(context.columns)}"
    )


if __name__ == "__main__":
    main()