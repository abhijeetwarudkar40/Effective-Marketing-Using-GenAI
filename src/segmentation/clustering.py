from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
import pandas as pd


def evaluate_kmeans(
    X,
    min_k=2,
    max_k=12,
    random_state=42
):

    results = []

    for k in range(
        min_k,
        max_k + 1
    ):

        model = KMeans(
            n_clusters=k,
            random_state=random_state,
            n_init=20
        )

        labels = model.fit_predict(X)

        silhouette = silhouette_score(
            X,
            labels
        )

        results.append({
            "k": k,
            "inertia": model.inertia_,
            "silhouette_score": silhouette
        })

    return pd.DataFrame(results)


def evaluate_kmeans_pca(
    X,
    min_k=2,
    max_k=12,
    variance_threshold=0.90,
    random_state=42
):

    # ---------------------------------------------------------
    # PCA
    # ---------------------------------------------------------

    pca_full = PCA()

    X_full = pca_full.fit_transform(X)

    cumulative_variance = (
        pca_full
        .explained_variance_ratio_
        .cumsum()
    )

    n_components = (
        cumulative_variance >= variance_threshold
    ).argmax() + 1

    pca = PCA(
        n_components=n_components
    )

    X_pca = pca.fit_transform(X)

    # ---------------------------------------------------------
    # K-MEANS
    # ---------------------------------------------------------

    results = []

    for k in range(
        min_k,
        max_k + 1
    ):

        model = KMeans(
            n_clusters=k,
            random_state=random_state,
            n_init=20
        )

        labels = model.fit_predict(
            X_pca
        )

        silhouette = silhouette_score(
            X_pca,
            labels
        )

        results.append({
            "k": k,
            "inertia": model.inertia_,
            "silhouette_score": silhouette
        })

    results = pd.DataFrame(results)

    return (
        results,
        X_pca,
        pca,
        n_components
    )


def train_kmeans(
    X,
    n_clusters,
    random_state=42
):

    model = KMeans(
        n_clusters=n_clusters,
        random_state=random_state,
        n_init=20
    )

    labels = model.fit_predict(X)

    return model, labels