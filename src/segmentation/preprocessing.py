import pandas as pd
import numpy as np

from sklearn.preprocessing import RobustScaler
from sklearn.impute import SimpleImputer


def prepare_clustering_data(df):

    data = df.copy()

    # ---------------------------------------------------------
    # CORE SEGMENTATION FEATURES
    # ---------------------------------------------------------
    #
    # We intentionally avoid highly redundant features.
    #
    # Each group represents a different behavioral dimension:
    #
    # VALUE
    # ACTIVITY
    # RECENCY
    # DIGITAL
    # PRODUCT RELATIONSHIP
    # ENGAGEMENT
    # RECOMMENDATION RESPONSE
    # LIFECYCLE / GROWTH
    # ---------------------------------------------------------

    feature_columns = [

        # -------------------------
        # CUSTOMER VALUE
        # -------------------------
        "annual_income",
        "average_account_balance",
        "monthly_spending",

        # -------------------------
        # TRANSACTION BEHAVIOR
        # -------------------------
        "transaction_count",
        "average_transaction_amount",

        # -------------------------
        # RECENCY
        # -------------------------
        "recency_days",

        # -------------------------
        # DIGITAL
        # -------------------------
        "digital_usage_score",

        # -------------------------
        # PRODUCT RELATIONSHIP
        # -------------------------
        "products_held",
        "product_categories_held",

        # -------------------------
        # CAMPAIGN ENGAGEMENT
        # -------------------------
        "engagement_score",

        # -------------------------
        # RECOMMENDATION BEHAVIOR
        # -------------------------
        "average_suitability_score",
        "recommendation_acceptance_rate",

        # -------------------------
        # FINANCIAL BEHAVIOR
        # -------------------------
        "debit_ratio",
        "credit_ratio",

        # -------------------------
        # LIFECYCLE / GROWTH
        # -------------------------
        "spending_trend",
    ]

    feature_columns = [
        column
        for column in feature_columns
        if column in data.columns
    ]

    X = data[feature_columns].copy()

    # ---------------------------------------------------------
    # REPLACE INF
    # ---------------------------------------------------------

    X = X.replace(
        [np.inf, -np.inf],
        np.nan
    )

    # ---------------------------------------------------------
    # IMPUTATION
    # ---------------------------------------------------------

    imputer = SimpleImputer(
        strategy="median"
    )

    X = pd.DataFrame(
        imputer.fit_transform(X),
        columns=feature_columns,
        index=data.index
    )

    # ---------------------------------------------------------
    # LOG TRANSFORMATION
    # ---------------------------------------------------------
    #
    # Financial and transaction variables are usually
    # right-skewed.
    # ---------------------------------------------------------

    log_features = [
        "annual_income",
        "average_account_balance",
        "monthly_spending",
        "transaction_count",
        "average_transaction_amount",
        "products_held",
        "product_categories_held",
    ]

    for column in log_features:

        if column in X.columns:

            X[column] = np.log1p(
                X[column].clip(lower=0)
            )

    # ---------------------------------------------------------
    # ROBUST SCALING
    # ---------------------------------------------------------
    #
    # More resistant to extreme financial customers than
    # ordinary StandardScaler.
    # ---------------------------------------------------------

    scaler = RobustScaler()

    X_scaled = scaler.fit_transform(X)

    X_scaled = pd.DataFrame(
        X_scaled,
        columns=feature_columns,
        index=data.index
    )

    return (
        X_scaled,
        feature_columns,
        scaler,
        imputer
    )