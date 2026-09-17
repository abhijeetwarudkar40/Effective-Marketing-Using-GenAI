import pandas as pd
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

PROCESSED_DIR = BASE_DIR / "data" / "processed"

INPUT_FILE = PROCESSED_DIR / "campaign_content.csv"
OUTPUT_FILE = PROCESSED_DIR / "campaign_ab_variants.csv"


# ============================================================
# LOAD CAMPAIGN CONTENT
# ============================================================

def load_campaign_content():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Campaign content file not found:\n{INPUT_FILE}"
        )

    return pd.read_csv(INPUT_FILE)


# ============================================================
# VARIANT A - VALUE / PERSONALIZATION
# ============================================================

def generate_variant_a(row):

    product = row.get("product_name", "our product")
    objective = row.get("campaign_objective", "Engagement")
    segment = row.get("primary_segment", "Core Active")

    if objective == "Cross-Sell":

        subject = f"Discover more value with {product}"

        headline = (
            f"A product selected with your financial needs in mind"
        )

        body = (
            f"As a valued {segment} customer, "
            f"{product} could complement your existing financial "
            f"relationship with us. Explore the potential benefits "
            f"and see whether it fits your goals."
        )

        cta = f"Explore {product}"

    elif objective == "Retention":

        subject = "We're here to support your financial journey"

        headline = (
            f"Make more of your relationship with us"
        )

        body = (
            f"We value your relationship with us. "
            f"{product} may provide an opportunity to get more "
            f"value from the financial services available to you."
        )

        cta = "Discover your benefits"

    elif objective == "Upsell":

        subject = f"Discover more with {product}"

        headline = (
            f"Take your financial experience to the next level"
        )

        body = (
            f"As a valued customer, you may benefit from the "
            f"additional value and features available through "
            f"{product}."
        )

        cta = f"Explore {product}"

    else:

        subject = f"A financial opportunity selected for you"

        headline = f"Explore {product}"

        body = (
            f"Based on your customer profile, "
            f"{product} may be relevant to your financial needs. "
            f"Take a closer look and discover whether it is right "
            f"for you."
        )

        cta = f"Learn more"


    return {
        "variant": "A",
        "strategy": "Value & Personalization",
        "subject_line": subject,
        "headline": headline,
        "body": body,
        "call_to_action": cta,
    }


# ============================================================
# VARIANT B - ACTION / DIRECT RESPONSE
# ============================================================

def generate_variant_b(row):

    product = row.get("product_name", "our product")
    objective = row.get("campaign_objective", "Engagement")

    if objective == "Cross-Sell":

        subject = f"Ready to explore {product}?"

        headline = (
            f"Your next financial product could be {product}"
        )

        body = (
            f"You already have a relationship with us. "
            f"Now you can explore {product} and see how it "
            f"could add value to your financial portfolio. "
            f"Take the next step today."
        )

        cta = f"Get started"

    elif objective == "Retention":

        subject = "Don't miss the value available to you"

        headline = (
            f"Make the most of your banking relationship"
        )

        body = (
            f"Now is a good time to review the opportunities "
            f"available to you. Explore {product} and take "
            f"action toward your financial goals."
        )

        cta = "Take action"

    elif objective == "Upsell":

        subject = f"Upgrade your financial experience today"

        headline = (
            f"More features. More value. Explore {product}."
        )

        body = (
            f"Looking for more from your financial relationship? "
            f"Explore {product} today and discover the additional "
            f"value it can offer."
        )

        cta = "Upgrade now"

    else:

        subject = f"Explore {product} today"

        headline = (
            f"Take the next step with {product}"
        )

        body = (
            f"{product} could be a relevant addition to your "
            f"financial journey. Explore the product today and "
            f"see what it can offer you."
        )

        cta = "Get started"


    return {
        "variant": "B",
        "strategy": "Action & Direct Response",
        "subject_line": subject,
        "headline": headline,
        "body": body,
        "call_to_action": cta,
    }


# ============================================================
# BUILD A/B VARIANTS
# ============================================================

def build_ab_variants(df):

    campaigns = []

    for _, row in df.iterrows():

        base_data = {
            "customer_id": row["customer_id"],
            "campaign_objective": row.get(
                "campaign_objective",
                "Engagement"
            ),
            "product_name": row.get(
                "product_name",
                "our product"
            ),
            "primary_segment": row.get(
                "primary_segment",
                "Core Active"
            ),
            "customer_persona": row.get(
                "customer_persona",
                "Customer"
            ),
            "retention_risk": row.get(
                "retention_risk",
                "Low Risk"
            ),
            "cross_sell_opportunity": row.get(
                "cross_sell_opportunity",
                "Moderate Cross-Sell Opportunity"
            ),
        }

        # ----------------------------
        # VARIANT A
        # ----------------------------

        variant_a = generate_variant_a(row)

        campaigns.append({
            **base_data,
            **variant_a
        })

        # ----------------------------
        # VARIANT B
        # ----------------------------

        variant_b = generate_variant_b(row)

        campaigns.append({
            **base_data,
            **variant_b
        })

    return pd.DataFrame(campaigns)


# ============================================================
# VALIDATION
# ============================================================

def validate_variants(df):

    print()
    print("=" * 70)
    print("A/B VARIANT VALIDATION")
    print("=" * 70)

    print()

    total_rows = len(df)

    unique_customers = df["customer_id"].nunique()

    print(
        f"Total campaign variants : {total_rows:,}"
    )

    print(
        f"Unique customers        : {unique_customers:,}"
    )

    print()

    # --------------------------------------------------------
    # VARIANT DISTRIBUTION
    # --------------------------------------------------------

    print("Variant Distribution")
    print("-" * 70)

    print(
        df["variant"].value_counts()
    )

    # --------------------------------------------------------
    # DUPLICATES
    # --------------------------------------------------------

    duplicate_pairs = (
        df.duplicated(
            subset=["customer_id", "variant"]
        ).sum()
    )

    print()
    print(
        f"Duplicate customer-variant pairs : "
        f"{duplicate_pairs}"
    )

    # --------------------------------------------------------
    # MISSING CONTENT
    # --------------------------------------------------------

    content_columns = [
        "subject_line",
        "headline",
        "body",
        "call_to_action",
    ]

    missing_content = (
        df[content_columns]
        .isna()
        .any(axis=1)
        .sum()
    )

    print(
        f"Missing campaign content : "
        f"{missing_content}"
    )

    # --------------------------------------------------------
    # CUSTOMERS WITH BOTH VARIANTS
    # --------------------------------------------------------

    variant_counts = (
        df.groupby("customer_id")["variant"]
        .nunique()
    )

    customers_with_both = (
        (variant_counts == 2).sum()
    )

    customers_missing_variant = (
        (variant_counts != 2).sum()
    )

    print(
        f"Customers with A + B variants : "
        f"{customers_with_both:,}"
    )

    print(
        f"Customers missing a variant   : "
        f"{customers_missing_variant:,}"
    )

    # --------------------------------------------------------
    # DIFFERENT CONTENT CHECK
    # --------------------------------------------------------

    pivot = (
        df.pivot(
            index="customer_id",
            columns="variant",
            values="body"
        )
    )

    identical_bodies = 0

    if "A" in pivot.columns and "B" in pivot.columns:

        identical_bodies = (
            pivot["A"] == pivot["B"]
        ).sum()

    print(
        f"Customers with identical A/B body : "
        f"{identical_bodies}"
    )

    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    passed = (
        duplicate_pairs == 0
        and missing_content == 0
        and customers_missing_variant == 0
        and identical_bodies == 0
    )

    print()

    if passed:

        print(
            "PASS - A/B variant validation successful"
        )

    else:

        print(
            "WARNING - A/B variant validation requires review"
        )

    return passed


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("PHASE 5D - A/B CAMPAIGN VARIANT GENERATION")
    print("=" * 70)

    print()

    # --------------------------------------------------------
    # LOAD
    # --------------------------------------------------------

    df = load_campaign_content()

    print(
        f"Campaign contents loaded : {len(df):,}"
    )

    print(
        f"Unique customers         : "
        f"{df['customer_id'].nunique():,}"
    )

    print()

    # --------------------------------------------------------
    # GENERATE
    # --------------------------------------------------------

    print(
        "Generating Variant A and Variant B..."
    )

    output = build_ab_variants(df)

    # --------------------------------------------------------
    # VALIDATE
    # --------------------------------------------------------

    validate_variants(output)

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    output.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print()
    print("=" * 70)
    print("PHASE 5D COMPLETE")
    print("=" * 70)

    print()

    print("Saved to:")
    print(OUTPUT_FILE)

    print()

    print(
        f"Rows    : {len(output):,}"
    )

    print(
        f"Columns : {len(output.columns)}"
    )

    print()

    # --------------------------------------------------------
    # SAMPLE
    # --------------------------------------------------------

    print("=" * 70)
    print("SAMPLE A/B CAMPAIGN")
    print("=" * 70)

    sample_customer = output["customer_id"].iloc[0]

    sample = output[
        output["customer_id"] == sample_customer
    ]

    for _, row in sample.iterrows():

        print()
        print(
            f"Customer : {row['customer_id']}"
        )

        print(
            f"Variant  : {row['variant']}"
        )

        print(
            f"Strategy : {row['strategy']}"
        )

        print(
            f"Product  : {row['product_name']}"
        )

        print(
            f"Subject  : {row['subject_line']}"
        )

        print(
            f"Headline : {row['headline']}"
        )

        print(
            f"CTA      : {row['call_to_action']}"
        )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()