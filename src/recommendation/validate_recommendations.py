from pathlib import Path
import pandas as pd


PROCESSED_DIR = Path("data/processed")
RAW_DIR = Path("data/raw")


def check_required_columns(df, required, name):
    missing = [c for c in required if c not in df.columns]

    if missing:
        raise ValueError(
            f"{name} is missing required columns: {missing}"
        )


def main():

    print("=" * 70)
    print("PHASE 4D - RECOMMENDATION QUALITY VALIDATION")
    print("=" * 70)

    # ---------------------------------------------------------
    # LOAD DATA
    # ---------------------------------------------------------

    print("\nLoading recommendation datasets...")

    recommendations = pd.read_csv(
        PROCESSED_DIR / "customer_recommendations.csv"
    )

    eligibility = pd.read_csv(
        PROCESSED_DIR / "customer_product_eligibility.csv"
    )

    scores = pd.read_csv(
        PROCESSED_DIR / "customer_product_scores.csv"
    )

    customers = pd.read_csv(
        RAW_DIR / "customers.csv"
    )

    products = pd.read_csv(
        RAW_DIR / "products.csv"
    )

    print(f"Recommendations : {len(recommendations):,}")
    print(f"Customers       : {customers['customer_id'].nunique():,}")
    print(f"Products        : {products['product_id'].nunique():,}")

    # ---------------------------------------------------------
    # REQUIRED COLUMNS
    # ---------------------------------------------------------

    check_required_columns(
        recommendations,
        [
            "customer_id",
            "product_id",
            "product_name",
            "recommendation_score",
            "recommendation_rank",
            "recommendation_confidence",
        ],
        "customer_recommendations"
    )

    check_required_columns(
        eligibility,
        [
            "customer_id",
            "product_id",
            "eligible",
            "already_owned",
        ],
        "customer_product_eligibility"
    )

    check_required_columns(
        scores,
        [
            "customer_id",
            "product_id",
            "recommendation_score",
        ],
        "customer_product_scores"
    )

    # ---------------------------------------------------------
    # 1. DUPLICATE CHECK
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print("1. DUPLICATE RECOMMENDATION CHECK")
    print("-" * 70)

    duplicate_pairs = recommendations.duplicated(
        subset=["customer_id", "product_id"]
    ).sum()

    print(f"Duplicate customer-product pairs : {duplicate_pairs}")

    if duplicate_pairs == 0:
        print("PASS - No duplicate recommendations")
    else:
        print("FAIL - Duplicate recommendations found")

    # ---------------------------------------------------------
    # 2. ELIGIBILITY VALIDATION
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print("2. PRODUCT ELIGIBILITY VALIDATION")
    print("-" * 70)

    eligibility_lookup = eligibility[
        [
            "customer_id",
            "product_id",
            "eligible",
            "already_owned",
        ]
    ].copy()

    validation = recommendations.merge(
        eligibility_lookup,
        on=["customer_id", "product_id"],
        how="left"
    )

    missing_eligibility = validation["eligible"].isna().sum()

    owned_recommendations = (
        validation["already_owned"].fillna(0).astype(int) == 1
    ).sum()

    ineligible_recommendations = (
        validation["eligible"].fillna(0).astype(int) != 1
    ).sum()

    print(
        f"Recommendations without eligibility record : "
        f"{missing_eligibility}"
    )

    print(
        f"Already-owned products recommended          : "
        f"{owned_recommendations}"
    )

    print(
        f"Ineligible products recommended              : "
        f"{ineligible_recommendations}"
    )

    if missing_eligibility == 0:
        print("PASS - All recommendations have eligibility records")
    else:
        print("FAIL - Missing eligibility records")

    if owned_recommendations == 0:
        print("PASS - No already-owned products recommended")
    else:
        print("FAIL - Already-owned products recommended")

    if ineligible_recommendations == 0:
        print("PASS - All recommendations are eligible")
    else:
        print("FAIL - Ineligible products recommended")

    # ---------------------------------------------------------
    # 3. CUSTOMER COVERAGE
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print("3. CUSTOMER COVERAGE")
    print("-" * 70)

    total_customers = customers["customer_id"].nunique()

    recommended_customers = recommendations[
        "customer_id"
    ].nunique()

    customers_without_recommendations = (
        set(customers["customer_id"])
        - set(recommendations["customer_id"])
    )

    coverage = (
        recommended_customers / total_customers * 100
    )

    print(f"Total customers                 : {total_customers}")
    print(f"Customers with recommendations : {recommended_customers}")
    print(f"Coverage                        : {coverage:.2f}%")
    print(
        f"Customers without recommendations : "
        f"{len(customers_without_recommendations)}"
    )

    # ---------------------------------------------------------
    # 4. TOP-N RANK VALIDATION
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print("4. TOP-N RANK VALIDATION")
    print("-" * 70)

    max_rank = recommendations[
        "recommendation_rank"
    ].max()

    invalid_ranks = recommendations[
        ~recommendations["recommendation_rank"].between(1, 3)
    ].shape[0]

    duplicate_ranks = (
        recommendations
        .duplicated(
            subset=["customer_id", "recommendation_rank"]
        )
        .sum()
    )

    print(f"Maximum recommendation rank : {max_rank}")
    print(f"Invalid ranks                : {invalid_ranks}")
    print(f"Duplicate customer-ranks     : {duplicate_ranks}")

    if invalid_ranks == 0:
        print("PASS - All recommendations are within Top-3")
    else:
        print("FAIL - Invalid recommendation ranks found")

    if duplicate_ranks == 0:
        print("PASS - No duplicate ranks per customer")
    else:
        print("FAIL - Duplicate ranks found")

    # ---------------------------------------------------------
    # 5. SCORE ORDER VALIDATION
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print("5. RECOMMENDATION SCORE ORDER")
    print("-" * 70)

    score_order_failures = 0

    for customer_id, group in recommendations.groupby(
        "customer_id"
    ):

        ordered = group.sort_values(
            "recommendation_rank"
        )

        scores_by_rank = ordered[
            "recommendation_score"
        ].tolist()

        for i in range(len(scores_by_rank) - 1):

            if scores_by_rank[i] < scores_by_rank[i + 1]:
                score_order_failures += 1
                break

    print(
        f"Customers violating score ordering : "
        f"{score_order_failures}"
    )

    if score_order_failures == 0:
        print("PASS - Recommendation scores follow rank order")
    else:
        print(
            "WARNING - Some rankings do not follow score order"
        )

    # ---------------------------------------------------------
    # 6. CONFIDENCE VALIDATION
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print("6. CONFIDENCE VALIDATION")
    print("-" * 70)

    valid_confidence = {
        "Low",
        "Medium",
        "High"
    }

    invalid_confidence = recommendations[
        ~recommendations[
            "recommendation_confidence"
        ].isin(valid_confidence)
    ].shape[0]

    print(
        f"Invalid confidence values : "
        f"{invalid_confidence}"
    )

    print("\nConfidence distribution:")

    print(
        recommendations[
            "recommendation_confidence"
        ].value_counts()
    )

    if invalid_confidence == 0:
        print("PASS - Confidence values are valid")
    else:
        print("FAIL - Invalid confidence values found")

    # ---------------------------------------------------------
    # 7. PRODUCT DISTRIBUTION
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print("7. PRODUCT RECOMMENDATION DISTRIBUTION")
    print("-" * 70)

    product_distribution = (
        recommendations[
            "product_name"
        ]
        .value_counts()
        .rename_axis("product_name")
        .reset_index(name="recommendation_count")
    )

    product_distribution["percentage"] = (
        product_distribution["recommendation_count"]
        / len(recommendations)
        * 100
    )

    print(
        product_distribution.to_string(
            index=False,
            formatters={
                "percentage": "{:.2f}".format
            }
        )
    )

    # ---------------------------------------------------------
    # 8. PRIMARY RECOMMENDATION DISTRIBUTION
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print("8. PRIMARY RECOMMENDATION DISTRIBUTION")
    print("-" * 70)

    primary = recommendations[
        recommendations["recommendation_rank"] == 1
    ]

    primary_distribution = (
        primary["product_name"]
        .value_counts()
        .rename_axis("product_name")
        .reset_index(name="primary_recommendations")
    )

    primary_distribution["percentage"] = (
        primary_distribution["primary_recommendations"]
        / len(primary)
        * 100
    )

    print(
        primary_distribution.to_string(
            index=False,
            formatters={
                "percentage": "{:.2f}".format
            }
        )
    )

    # ---------------------------------------------------------
    # 9. SCORE QUALITY
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print("9. RECOMMENDATION SCORE QUALITY")
    print("-" * 70)

    print(
        recommendations[
            "recommendation_score"
        ].describe().round(4)
    )

    # ---------------------------------------------------------
    # 10. CUSTOMER RECOMMENDATION COUNT
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print("10. RECOMMENDATIONS PER CUSTOMER")
    print("-" * 70)

    recommendation_counts = (
        recommendations
        .groupby("customer_id")
        .size()
    )

    print(
        recommendation_counts.describe().round(2)
    )

    invalid_customer_counts = (
        (recommendation_counts < 1)
        | (recommendation_counts > 3)
    ).sum()

    print(
        f"\nCustomers outside 1-3 recommendations : "
        f"{invalid_customer_counts}"
    )

    # ---------------------------------------------------------
    # 11. SEGMENT × PRODUCT ANALYSIS
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print("11. SEGMENT × PRODUCT RECOMMENDATION")
    print("-" * 70)

    if "primary_segment" in recommendations.columns:

        segment_product = pd.crosstab(
            recommendations["primary_segment"],
            recommendations["product_name"]
        )

        print(segment_product.to_string())

    else:
        print(
            "WARNING - primary_segment not available"
        )

    # ---------------------------------------------------------
    # 12. PERSONA × PRODUCT ANALYSIS
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print("12. PERSONA × PRODUCT RECOMMENDATION")
    print("-" * 70)

    if "customer_persona" in recommendations.columns:

        persona_product = pd.crosstab(
            recommendations["customer_persona"],
            recommendations["product_name"]
        )

        print(persona_product.to_string())

    else:
        print(
            "WARNING - customer_persona not available"
        )

    # ---------------------------------------------------------
    # 13. BUSINESS LOGIC CHECK
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print("13. BUSINESS LOGIC CHECK")
    print("-" * 70)

    business_warnings = []

    # Low confidence recommendations
    low_confidence_pct = (
        (
            recommendations[
                "recommendation_confidence"
            ] == "Low"
        ).mean()
        * 100
    )

    if low_confidence_pct > 80:
        business_warnings.append(
            "More than 80% of recommendations have Low confidence"
        )

    # Product concentration
    top_product_share = (
        recommendations["product_name"]
        .value_counts(normalize=True)
        .iloc[0]
        * 100
    )

    if top_product_share > 50:
        business_warnings.append(
            "One product represents more than 50% of recommendations"
        )

    # Score quality
    if recommendations[
        "recommendation_score"
    ].mean() < 0.30:
        business_warnings.append(
            "Average recommendation score is below 0.30"
        )

    if business_warnings:

        print("BUSINESS WARNINGS:")

        for warning in business_warnings:
            print(f"  - {warning}")

    else:
        print(
            "PASS - No major business logic warnings detected"
        )

    # ---------------------------------------------------------
    # 14. FINAL VALIDATION SUMMARY
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print("FINAL VALIDATION SUMMARY")
    print("=" * 70)

    checks = {
        "Duplicate recommendations": duplicate_pairs == 0,
        "Eligibility records": missing_eligibility == 0,
        "No already-owned products": owned_recommendations == 0,
        "All products eligible": ineligible_recommendations == 0,
        "Valid ranks": invalid_ranks == 0,
        "No duplicate ranks": duplicate_ranks == 0,
        "Valid confidence": invalid_confidence == 0,
        "Customer recommendation count": invalid_customer_counts == 0,
    }

    for name, passed in checks.items():

        status = "PASS" if passed else "FAIL"

        print(
            f"{status:<8} {name}"
        )

    passed_checks = sum(checks.values())
    total_checks = len(checks)

    print("\n" + "-" * 70)

    print(
        f"Validation score : "
        f"{passed_checks}/{total_checks}"
    )

    # ---------------------------------------------------------
    # SAVE VALIDATED DATA
    # ---------------------------------------------------------

    output_path = (
        PROCESSED_DIR /
        "validated_customer_recommendations.csv"
    )

    recommendations.to_csv(
        output_path,
        index=False
    )

    print("\nValidation output saved to:")
    print(output_path)

    print("\n" + "=" * 70)
    print("PHASE 4D COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()