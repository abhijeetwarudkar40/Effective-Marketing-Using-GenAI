from pathlib import Path

from src.data.loader import DatasetLoader

from src.features.engineering import (
    build_customer_360
)


def main():

    print("=" * 70)
    print("PERSONALIZED MARKETING AI")
    print("PHASE 2 - FEATURE ENGINEERING")
    print("=" * 70)

    # ---------------------------------------------------------
    # LOAD DATA
    # ---------------------------------------------------------

    loader = DatasetLoader()

    datasets = loader.load_all()

    print("\nDatasets loaded successfully.")

    for name, df in datasets.items():
        print(
            f"{name:<25} {len(df):>6} rows"
        )

    # ---------------------------------------------------------
    # BUILD CUSTOMER 360
    # ---------------------------------------------------------

    print("\nBuilding customer-level features...")

    customer_features = build_customer_360(
        customers=datasets["customers"],
        transactions=datasets["transactions"],
        product_holdings=datasets["product_holdings"],
        products=datasets["products"],
        campaign_interactions=datasets[
            "campaign_interactions"
        ],
        recommendations=datasets[
            "recommendations"
        ]
    )

    # ---------------------------------------------------------
    # CREATE OUTPUT DIRECTORY
    # ---------------------------------------------------------

    output_directory = Path(
        "data/processed"
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = (
        output_directory /
        "customer_features.csv"
    )

    # ---------------------------------------------------------
    # SAVE
    # ---------------------------------------------------------

    customer_features.to_csv(
        output_path,
        index=False
    )

    # ---------------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print("FEATURE ENGINEERING COMPLETED")
    print("=" * 70)

    print(
        f"\nCustomers: "
        f"{len(customer_features)}"
    )

    print(
        f"Features: "
        f"{len(customer_features.columns)}"
    )

    print(
        f"\nOutput saved to:\n"
        f"{output_path}"
    )

    print("\nFirst 5 rows:")

    print(
        customer_features.head()
        .to_string()
    )


if __name__ == "__main__":
    main()