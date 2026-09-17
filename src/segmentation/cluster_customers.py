import pandas as pd
import numpy as np

from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

from src.segmentation.preprocessing import (
    prepare_clustering_data
)


DATA_PATH = "data/processed/customer_features.csv"

OUTPUT_PATH = (
    "data/processed/customer_clusters.csv"
)


def main():

    print("=" * 70)
    print("PHASE 3C - CUSTOMER CLUSTERING")
    print("=" * 70)

    # ---------------------------------------------------------
    # LOAD DATA
    # ---------------------------------------------------------

    df = pd.read_csv(DATA_PATH)

    print(
        f"\nCustomers loaded: {len(df)}"
    )

    # ---------------------------------------------------------
    # PREPARE FEATURES
    # ---------------------------------------------------------

    (
        X,
        feature_columns,
        scaler,
        imputer
    ) = prepare_clustering_data(df)

    print(
        f"Features used: {len(feature_columns)}"
    )

    # ---------------------------------------------------------
    # PCA
    # ---------------------------------------------------------

    pca = PCA(
        n_components=7,
        random_state=42
    )

    X_pca = pca.fit_transform(X)

    explained_variance = (
        pca.explained_variance_ratio_.sum()
    )

    print(
        f"\nPCA components: 7"
    )

    print(
        f"Explained variance: "
        f"{explained_variance:.2%}"
    )

    # ---------------------------------------------------------
    # K-MEANS
    # ---------------------------------------------------------

    kmeans = KMeans(
        n_clusters=4,
        random_state=42,
        n_init=20
    )

    clusters = kmeans.fit_predict(
        X_pca
    )

    # ---------------------------------------------------------
    # ADD CLUSTER LABEL
    # ---------------------------------------------------------

    result = df.copy()

    result["cluster_id"] = clusters

    # ---------------------------------------------------------
    # CLUSTER SIZE
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print("CLUSTER SIZES")
    print("=" * 70)

    cluster_counts = (
        result["cluster_id"]
        .value_counts()
        .sort_index()
    )

    for cluster_id, count in cluster_counts.items():

        percentage = (
            count / len(result) * 100
        )

        print(
            f"Cluster {cluster_id}: "
            f"{count} customers "
            f"({percentage:.1f}%)"
        )

    # ---------------------------------------------------------
    # SAVE
    # ---------------------------------------------------------

    result.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print("\nSaved to:")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()