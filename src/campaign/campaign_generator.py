import pandas as pd
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

PROCESSED_DIR = BASE_DIR / "data" / "processed"

INPUT_FILE = PROCESSED_DIR / "campaign_context.csv"
OUTPUT_FILE = PROCESSED_DIR / "campaign_content.csv"


# ============================================================
# LOAD DATA
# ============================================================

def load_campaign_context():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Campaign context file not found:\n{INPUT_FILE}"
        )

    return pd.read_csv(INPUT_FILE)


# ============================================================
# CAMPAIGN CONTENT GENERATION
# ============================================================

def generate_campaign_content(row):

    customer_id = row["customer_id"]

    product = row.get(
        "product_name",
        "our financial product"
    )

    objective = row.get(
        "campaign_objective",
        "Engagement"
    )

    segment = row.get(
        "primary_segment",
        "Core Active"
    )

    persona = row.get(
        "customer_persona",
        "Customer"
    )

    retention_risk = row.get(
        "retention_risk",
        "Low Risk"
    )

    cross_sell = row.get(
        "cross_sell_opportunity",
        "Moderate Cross-Sell Opportunity"
    )

    # --------------------------------------------------------
    # OBJECTIVE BASED MESSAGING
    # --------------------------------------------------------

    if objective == "Cross-Sell":

        subject = f"Discover more value with {product}"

        headline = (
            f"Take the next step with {product}"
        )

        body = (
            f"Based on your relationship with us, "
            f"{product} could be a valuable addition to "
            f"your financial portfolio."
        )

        call_to_action = (
            f"Explore {product}"
        )

    elif objective == "Retention":

        subject = (
            f"We're here to support your financial journey"
        )

        headline = (
            "Keep getting more from your relationship with us"
        )

        body = (
            f"We value your relationship with us. "
            f"Explore how {product} can help you "
            f"get more value from your financial needs."
        )

        call_to_action = (
            f"Learn more about {product}"
        )

    elif objective == "Upsell":

        subject = (
            f"Take your banking experience further"
        )

        headline = (
            f"Upgrade your financial experience"
        )

        body = (
            f"As a valued customer, you may benefit from "
            f"the enhanced features and value offered by "
            f"{product}."
        )

        call_to_action = (
            f"Explore {product}"
        )

    else:

        subject = (
            f"A financial opportunity for you"
        )

        headline = (
            f"Explore {product}"
        )

        body = (
            f"We've identified {product} as a product "
            f"that may be relevant to your financial needs."
        )

        call_to_action = (
            f"Discover {product}"
        )

    # --------------------------------------------------------
    # RETURN CAMPAIGN
    # --------------------------------------------------------

    return {
        "customer_id": customer_id,
        "campaign_objective": objective,
        "product_name": product,
        "primary_segment": segment,
        "customer_persona": persona,
        "retention_risk": retention_risk,
        "cross_sell_opportunity": cross_sell,
        "subject_line": subject,
        "headline": headline,
        "body": body,
        "call_to_action": call_to_action,
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("PHASE 5C - CAMPAIGN CONTENT GENERATION")
    print("=" * 70)

    print()

    # --------------------------------------------------------
    # LOAD
    # --------------------------------------------------------

    df = load_campaign_context()

    print(
        f"Campaign contexts loaded : {len(df):,}"
    )

    print(
        f"Unique customers         : "
        f"{df['customer_id'].nunique():,}"
    )

    print()

    print("Generating campaign content...")

    # --------------------------------------------------------
    # GENERATE
    # --------------------------------------------------------

    campaigns = []

    for _, row in df.iterrows():

        campaign = generate_campaign_content(row)

        campaigns.append(campaign)

    output = pd.DataFrame(campaigns)

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("CAMPAIGN CONTENT VALIDATION")
    print("=" * 70)

    print()

    print(
        f"Campaigns generated : {len(output):,}"
    )

    print(
        f"Unique customers    : "
        f"{output['customer_id'].nunique():,}"
    )

    duplicate_customers = (
        output["customer_id"].duplicated().sum()
    )

    print(
        f"Duplicate customers : {duplicate_customers}"
    )

    missing_content = (
        output[
            [
                "subject_line",
                "headline",
                "body",
                "call_to_action",
            ]
        ]
        .isna()
        .any(axis=1)
        .sum()
    )

    print(
        f"Missing campaign content : {missing_content}"
    )

    # --------------------------------------------------------
    # OBJECTIVE DISTRIBUTION
    # --------------------------------------------------------

    print()
    print("Campaign Objective Distribution")
    print("-" * 70)

    print(
        output["campaign_objective"]
        .value_counts()
    )

    # --------------------------------------------------------
    # PRODUCT DISTRIBUTION
    # --------------------------------------------------------

    print()
    print("Campaign Product Distribution")
    print("-" * 70)

    print(
        output["product_name"]
        .value_counts()
    )

    # --------------------------------------------------------
    # VALIDATION RESULT
    # --------------------------------------------------------

    if (
        duplicate_customers == 0
        and missing_content == 0
    ):

        print()
        print(
            "PASS - Campaign content validation successful"
        )

    else:

        print()
        print(
            "WARNING - Campaign content requires review"
        )

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    output.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print()
    print("=" * 70)
    print("PHASE 5C COMPLETE")
    print("=" * 70)

    print()
    print("Saved to:")
    print(OUTPUT_FILE)

    print()
    print(f"Rows    : {len(output):,}")
    print(f"Columns : {len(output.columns)}")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()