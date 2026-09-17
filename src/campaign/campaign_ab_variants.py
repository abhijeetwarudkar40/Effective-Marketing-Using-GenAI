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
# VARIANT A - BENEFIT FOCUSED
# ============================================================

def generate_variant_a(row):
    """
    Generate Variant A.

    Strategy:
    Benefit-focused messaging.
    """

    product = row.get(
        "product_name",
        "our banking product"
    )

    objective = row.get(
        "campaign_objective",
        "Engagement"
    )

    if objective == "Retention":

        return {
            "subject": f"Discover more value with {product}",
            "headline": f"More value for your banking journey",
            "body": (
                f"Explore {product} and discover an option that "
                f"may complement your evolving financial needs."
            ),
            "cta": f"Explore {product}",
        }

    if objective == "Cross-Sell":

        return {
            "subject": f"Explore {product} for your financial needs",
            "headline": f"Discover another option for your financial journey",
            "body": (
                f"Based on your banking relationship, explore {product} "
                f"and see how it may complement your existing financial needs."
            ),
            "cta": f"Explore {product}",
        }

    if objective == "Upsell":

        return {
            "subject": f"Take your banking further with {product}",
            "headline": f"Explore more value with {product}",
            "body": (
                f"Discover {product} and explore how it may provide "
                f"additional value within your financial journey."
            ),
            "cta": f"Explore {product}",
        }

    return {
        "subject": f"Discover {product}",
        "headline": f"An option worth exploring",
        "body": (
            f"Explore {product} and learn how it may complement "
            f"your financial needs."
        ),
        "cta": "Learn More",
    }


# ============================================================
# VARIANT B - ACTION FOCUSED
# ============================================================

def generate_variant_b(row):
    """
    Generate Variant B.

    Strategy:
    Action-focused messaging.
    """

    product = row.get(
        "product_name",
        "our banking product"
    )

    objective = row.get(
        "campaign_objective",
        "Engagement"
    )

    if objective == "Retention":

        return {
            "subject": f"Keep exploring your options with {product}",
            "headline": f"Consider your next banking opportunity",
            "body": (
                f"Take a closer look at {product} and consider whether "
                f"it could be a suitable addition to your financial plans."
            ),
            "cta": "Learn More",
        }

    if objective == "Cross-Sell":

        return {
            "subject": f"Have you explored {product}?",
            "headline": f"Consider adding {product} to your financial plans",
            "body": (
                f"Take the next step and learn more about {product}. "
                f"Review the available information to see whether it "
                f"fits your financial needs."
            ),
            "cta": "Learn More",
        }

    if objective == "Upsell":

        return {
            "subject": f"Explore your {product} options",
            "headline": f"Take the next step with {product}",
            "body": (
                f"Learn more about {product} and explore whether it "
                f"could support your current financial goals."
            ),
            "cta": "Explore Options",
        }

    return {
        "subject": f"See what {product} can offer",
        "headline": f"Take a closer look at {product}",
        "body": (
            f"Learn more about {product} and consider whether it "
            f"could complement your financial needs."
        ),
        "cta": "Learn More",
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("PHASE 5D - A/B CAMPAIGN VARIANT GENERATION")
    print("=" * 70)

    # --------------------------------------------------------
    # LOAD CAMPAIGN CONTENT
    # --------------------------------------------------------

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"Campaign content not found:\n{INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    print()
    print(
        f"Campaigns loaded : {len(df):,}"
    )

    print(
        f"Unique customers : "
        f"{df['customer_id'].nunique():,}"
    )

    print()
    print(
        "Generating A/B campaign variants..."
    )
    print()

    # --------------------------------------------------------
    # GENERATE VARIANTS
    # --------------------------------------------------------

    results = []

    for index, row in df.iterrows():

        variant_a = generate_variant_a(row)
        variant_b = generate_variant_b(row)

        result = row.to_dict()

        # ----------------------------------------------------
        # VARIANT A
        # ----------------------------------------------------

        result.update(
            {
                "variant_a_subject":
                    variant_a["subject"],

                "variant_a_headline":
                    variant_a["headline"],

                "variant_a_body":
                    variant_a["body"],

                "variant_a_cta":
                    variant_a["cta"],
            }
        )

        # ----------------------------------------------------
        # VARIANT B
        # ----------------------------------------------------

        result.update(
            {
                "variant_b_subject":
                    variant_b["subject"],

                "variant_b_headline":
                    variant_b["headline"],

                "variant_b_body":
                    variant_b["body"],

                "variant_b_cta":
                    variant_b["cta"],
            }
        )

        # ----------------------------------------------------
        # STRATEGY
        # ----------------------------------------------------

        result["variant_a_strategy"] = (
            "Benefit-Focused"
        )

        result["variant_b_strategy"] = (
            "Action-Focused"
        )

        results.append(result)

        if (index + 1) % 50 == 0:

            print(
                f"Generated A/B variants: "
                f"{index + 1:,}/{len(df):,}"
            )

    output = pd.DataFrame(results)

    # ========================================================
    # VALIDATION
    # ========================================================

    print()
    print("=" * 70)
    print("A/B VARIANT VALIDATION")
    print("=" * 70)

    print()
    print(
        f"Total campaigns : {len(output):,}"
    )

    print(
        f"Unique customers: "
        f"{output['customer_id'].nunique():,}"
    )

    # --------------------------------------------------------
    # DUPLICATE CUSTOMERS
    # --------------------------------------------------------

    duplicate_customers = (
        output["customer_id"]
        .duplicated()
        .sum()
    )

    print(
        f"Duplicate customers: "
        f"{duplicate_customers:,}"
    )

    # --------------------------------------------------------
    # REQUIRED VARIANT COLUMNS
    # --------------------------------------------------------

    required_columns = [
        "variant_a_subject",
        "variant_a_headline",
        "variant_a_body",
        "variant_a_cta",
        "variant_b_subject",
        "variant_b_headline",
        "variant_b_body",
        "variant_b_cta",
    ]

    missing_content = 0

    for column in required_columns:

        missing_content += (
            output[column]
            .isna()
            .sum()
        )

        missing_content += (
            output[column]
            .astype(str)
            .str.strip()
            .eq("")
            .sum()
        )

    print(
        f"Missing A/B content: "
        f"{missing_content:,}"
    )

    # --------------------------------------------------------
    # CHECK DIFFERENCE
    # --------------------------------------------------------

    identical_variants = (
        (
            output["variant_a_subject"]
            == output["variant_b_subject"]
        )
        &
        (
            output["variant_a_headline"]
            == output["variant_b_headline"]
        )
        &
        (
            output["variant_a_body"]
            == output["variant_b_body"]
        )
        &
        (
            output["variant_a_cta"]
            == output["variant_b_cta"]
        )
    ).sum()

    print(
        f"Identical A/B variants: "
        f"{identical_variants:,}"
    )

    # --------------------------------------------------------
    # STRATEGY DISTRIBUTION
    # --------------------------------------------------------

    print()
    print("Variant Strategy")
    print("-" * 70)

    print(
        output["variant_a_strategy"]
        .value_counts()
    )

    print(
        output["variant_b_strategy"]
        .value_counts()
    )

    # ========================================================
    # VALIDATION RESULT
    # ========================================================

    validation_pass = (
        duplicate_customers == 0
        and missing_content == 0
        and identical_variants == 0
    )

    print()

    if validation_pass:

        print(
            "PASS - A/B variant validation successful"
        )

    else:

        print(
            "WARNING - A/B variant validation "
            "found issues"
        )

    # ========================================================
    # SAVE
    # ========================================================

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
        f"Columns : {len(output.columns):,}"
    )

    # ========================================================
    # SAMPLE
    # ========================================================

    print()
    print("=" * 70)
    print("SAMPLE A/B CAMPAIGN")
    print("=" * 70)

    sample = output.iloc[0]

    print()
    print(
        f"Customer : {sample['customer_id']}"
    )

    print(
        f"Product  : {sample['product_name']}"
    )

    print(
        f"Objective: {sample['campaign_objective']}"
    )

    print()
    print("VARIANT A")
    print("-" * 70)

    print(
        f"Strategy : "
        f"{sample['variant_a_strategy']}"
    )

    print(
        f"Subject  : "
        f"{sample['variant_a_subject']}"
    )

    print(
        f"Headline : "
        f"{sample['variant_a_headline']}"
    )

    print(
        f"Body     : "
        f"{sample['variant_a_body']}"
    )

    print(
        f"CTA      : "
        f"{sample['variant_a_cta']}"
    )

    print()
    print("VARIANT B")
    print("-" * 70)

    print(
        f"Strategy : "
        f"{sample['variant_b_strategy']}"
    )

    print(
        f"Subject  : "
        f"{sample['variant_b_subject']}"
    )

    print(
        f"Headline : "
        f"{sample['variant_b_headline']}"
    )

    print(
        f"Body     : "
        f"{sample['variant_b_body']}"
    )

    print(
        f"CTA      : "
        f"{sample['variant_b_cta']}"
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()