import pandas as pd

from src.segmentation.preprocessing import (
    prepare_clustering_data
)

from src.segmentation.clustering import (
    evaluate_kmeans,
    evaluate_kmeans_pca
)


DATA_PATH = (
    "data/processed/customer_features.csv"
)


def main():

    print("=" * 70)
    print("PHASE 3 - CUSTOMER SEGMENTATION")
    print("IMPROVED CLUSTER EVALUATION")
    print("=" * 70)

    # ---------------------------------------------------------
    # LOAD
    # ---------------------------------------------------------

    df = pd.read_csv(DATA_PATH)

    print(
        f"\nCustomers loaded: {len(df)}"
    )

    print(
        f"Available features: {len(df.columns)}"
    )

    # ---------------------------------------------------------
    # PREPARE
    # ---------------------------------------------------------

    (
        X,
        feature_columns,
        scaler,
        imputer
    ) = prepare_clustering_data(df)

    print(
        f"\nFeatures used: {len(feature_columns)}"
    )

    for feature in feature_columns:
        print(f"  - {feature}")

    # ---------------------------------------------------------
    # NORMAL K-MEANS
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print("ROBUST-SCALED K-MEANS")
    print("=" * 70)

    results = evaluate_kmeans(
        X,
        min_k=2,
        max_k=12
    )

    print(
        results.to_string(
            index=False
        )
    )

    # ---------------------------------------------------------
    # PCA K-MEANS
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print("PCA + K-MEANS")
    print("=" * 70)

    (
        pca_results,
        X_pca,
        pca,
        n_components
    ) = evaluate_kmeans_pca(
        X,
        min_k=2,
        max_k=12,
        variance_threshold=0.90
    )

    print(
        f"\nPCA components retaining "
        f"90% variance: {n_components}"
    )

    print()

    print(
        pca_results.to_string(
            index=False
        )
    )

    # ---------------------------------------------------------
    # BEST RESULTS
    # ---------------------------------------------------------

    best_normal = results.loc[
        results["silhouette_score"].idxmax()
    ]

    best_pca = pca_results.loc[
        pca_results["silhouette_score"].idxmax()
    ]

    print("\n" + "=" * 70)
    print("BEST RESULTS")
    print("=" * 70)

    print(
        f"\nRobust K-Means:"
        f"\n  K = {int(best_normal['k'])}"
        f"\n  Silhouette = "
        f"{best_normal['silhouette_score']:.4f}"
    )

    print(
        f"\nPCA + K-Means:"
        f"\n  K = {int(best_pca['k'])}"
        f"\n  Silhouette = "
        f"{best_pca['silhouette_score']:.4f}"
    )

    # ---------------------------------------------------------
    # SAVE
    # ---------------------------------------------------------

    results.to_csv(
        "data/processed/"
        "cluster_evaluation_robust.csv",
        index=False
    )

    pca_results.to_csv(
        "data/processed/"
        "cluster_evaluation_pca.csv",
        index=False
    )

    print(
        "\nEvaluation files saved."
    )


if __name__ == "__main__":
    main()