import pandas as pd
import numpy as np


def safe_divide(numerator, denominator):
    """
    Safely divide two pandas Series.
    Returns 0 when denominator is 0.
    """
    return numerator.div(denominator.replace(0, np.nan)).fillna(0)


def engineer_transaction_features(transactions):
    """
    Convert transaction-level data into customer-level behavioral features.
    """

    df = transactions.copy()

    # ---------------------------------------------------------
    # DATE CLEANING
    # ---------------------------------------------------------

    df["transaction_date"] = pd.to_datetime(
        df["transaction_date"],
        errors="coerce"
    )

    df["amount"] = pd.to_numeric(
        df["amount"],
        errors="coerce"
    ).fillna(0)

    # Remove invalid transaction dates
    df = df.dropna(subset=["transaction_date"])

    # ---------------------------------------------------------
    # BASIC TRANSACTION FEATURES
    # ---------------------------------------------------------

    grouped = df.groupby("customer_id")

    features = grouped.agg(
        transaction_count=("transaction_id", "count"),
        total_transaction_amount=("amount", "sum"),
        average_transaction_amount=("amount", "mean"),
        median_transaction_amount=("amount", "median"),
        maximum_transaction_amount=("amount", "max"),
        minimum_transaction_amount=("amount", "min"),
        transaction_std=("amount", "std"),
        active_months=(
            "transaction_date",
            lambda x: x.dt.to_period("M").nunique()
        ),
        first_transaction_date=("transaction_date", "min"),
        last_transaction_date=("transaction_date", "max"),
    ).reset_index()

    features["transaction_std"] = (
        features["transaction_std"]
        .fillna(0)
    )

    # ---------------------------------------------------------
    # RECENCY
    # ---------------------------------------------------------

    analysis_date = df["transaction_date"].max()

    features["recency_days"] = (
        analysis_date -
        features["last_transaction_date"]
    ).dt.days

    # ---------------------------------------------------------
    # TRANSACTION FREQUENCY
    # ---------------------------------------------------------

    features["transactions_per_active_month"] = safe_divide(
        features["transaction_count"],
        features["active_months"]
    )

    # ---------------------------------------------------------
    # DEBIT / CREDIT BEHAVIOR
    # ---------------------------------------------------------

    debit = (
        df[df["debit_credit"].str.lower() == "debit"]
        .groupby("customer_id")["amount"]
        .agg(
            debit_transaction_count="count",
            debit_total_amount="sum",
            debit_average_amount="mean"
        )
        .reset_index()
    )

    credit = (
        df[df["debit_credit"].str.lower() == "credit"]
        .groupby("customer_id")["amount"]
        .agg(
            credit_transaction_count="count",
            credit_total_amount="sum",
            credit_average_amount="mean"
        )
        .reset_index()
    )

    features = features.merge(
        debit,
        on="customer_id",
        how="left"
    )

    features = features.merge(
        credit,
        on="customer_id",
        how="left"
    )

    numeric_columns = [
        "debit_transaction_count",
        "debit_total_amount",
        "debit_average_amount",
        "credit_transaction_count",
        "credit_total_amount",
        "credit_average_amount",
    ]

    features[numeric_columns] = (
        features[numeric_columns]
        .fillna(0)
    )

    # ---------------------------------------------------------
    # RATIOS
    # ---------------------------------------------------------

    features["debit_ratio"] = safe_divide(
        features["debit_transaction_count"],
        features["transaction_count"]
    )

    features["credit_ratio"] = safe_divide(
        features["credit_transaction_count"],
        features["transaction_count"]
    )

    # ---------------------------------------------------------
    # TRANSACTION TYPE FEATURES
    # ---------------------------------------------------------

    transaction_type_counts = pd.crosstab(
        df["customer_id"],
        df["transaction_type"]
    )

    transaction_type_counts.columns = [
        "transaction_type_" + str(col).lower().replace(" ", "_")
        for col in transaction_type_counts.columns
    ]

    transaction_type_counts = (
        transaction_type_counts
        .reset_index()
    )

    features = features.merge(
        transaction_type_counts,
        on="customer_id",
        how="left"
    )

    # ---------------------------------------------------------
    # PAYMENT CHANNEL FEATURES
    # ---------------------------------------------------------

    channel_counts = pd.crosstab(
        df["customer_id"],
        df["payment_channel"]
    )

    channel_counts.columns = [
        "channel_" + str(col).lower().replace(" ", "_")
        for col in channel_counts.columns
    ]

    channel_counts = (
        channel_counts
        .reset_index()
    )

    features = features.merge(
        channel_counts,
        on="customer_id",
        how="left"
    )

    # ---------------------------------------------------------
    # MERCHANT CATEGORY FEATURES
    # ---------------------------------------------------------

    category_spending = pd.pivot_table(
        df,
        index="customer_id",
        columns="merchant_category",
        values="amount",
        aggfunc="sum",
        fill_value=0
    )

    category_spending.columns = [
        "spending_" + str(col).lower().replace(" ", "_")
        for col in category_spending.columns
    ]

    category_spending = (
        category_spending
        .reset_index()
    )

    features = features.merge(
        category_spending,
        on="customer_id",
        how="left"
    )

    # ---------------------------------------------------------
    # CATEGORY AFFINITY
    # ---------------------------------------------------------

    category_totals = (
        df.groupby(
            ["customer_id", "merchant_category"]
        )["amount"]
        .sum()
        .reset_index()
    )

    preferred_category = (
        category_totals
        .sort_values(
            ["customer_id", "amount"],
            ascending=[True, False]
        )
        .drop_duplicates("customer_id")
        [["customer_id", "merchant_category"]]
        .rename(
            columns={
                "merchant_category": "preferred_merchant_category"
            }
        )
    )

    features = features.merge(
        preferred_category,
        on="customer_id",
        how="left"
    )

    # ---------------------------------------------------------
    # PAYMENT CHANNEL AFFINITY
    # ---------------------------------------------------------

    channel_totals = (
        df.groupby(
            ["customer_id", "payment_channel"]
        )["amount"]
        .sum()
        .reset_index()
    )

    preferred_channel = (
        channel_totals
        .sort_values(
            ["customer_id", "amount"],
            ascending=[True, False]
        )
        .drop_duplicates("customer_id")
        [["customer_id", "payment_channel"]]
        .rename(
            columns={
                "payment_channel": "preferred_transaction_channel"
            }
        )
    )

    features = features.merge(
        preferred_channel,
        on="customer_id",
        how="left"
    )

    # ---------------------------------------------------------
    # MONTHLY SPENDING TREND
    # ---------------------------------------------------------

    monthly = (
        df.assign(
            month=df["transaction_date"].dt.to_period("M")
        )
        .groupby(
            ["customer_id", "month"]
        )["amount"]
        .sum()
        .reset_index()
    )

    def calculate_trend(group):

        if len(group) < 2:
            return 0

        values = group["amount"].values

        x = np.arange(len(values))

        slope = np.polyfit(x, values, 1)[0]

        return slope

    trend = (
        monthly
        .sort_values(["customer_id", "month"])
        .groupby("customer_id")
        .apply(calculate_trend, include_groups=False)
        .rename("spending_trend")
        .reset_index()
    )

    features = features.merge(
        trend,
        on="customer_id",
        how="left"
    )

    return features

def engineer_customer_features(customers):
    """
    Clean and prepare customer-level profile attributes.
    """

    df = customers.copy()

    numeric_columns = [
        "age",
        "annual_income",
        "credit_score",
        "account_tenure_years",
        "average_account_balance",
        "monthly_spending",
        "monthly_transactions",
        "digital_usage_score",
    ]

    for column in numeric_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        df[column] = df[column].fillna(
            df[column].median()
        )

    categorical_columns = [
        "gender",
        "city",
        "occupation",
        "risk_appetite",
        "investment_preference",
        "preferred_channel",
        "preferred_language",
    ]

    for column in categorical_columns:

        df[column] = (
            df[column]
            .fillna("Unknown")
            .astype(str)
            .str.strip()
        )

    # ---------------------------------------------------------
    # CUSTOMER VALUE FEATURES
    # ---------------------------------------------------------

    df["income_to_spending_ratio"] = safe_divide(
        df["annual_income"],
        df["monthly_spending"] * 12
    )

    df["balance_to_income_ratio"] = safe_divide(
        df["average_account_balance"],
        df["annual_income"]
    )

    return df

def engineer_product_features(product_holdings, products):
    """
    Convert product holdings into customer-level product features.
    """

    holdings = product_holdings.copy()
    catalog = products.copy()

    holdings["opened_date"] = pd.to_datetime(
        holdings["opened_date"],
        errors="coerce"
    )

    # Number of products owned
    product_count = (
        holdings.groupby("customer_id")
        .agg(
            products_held=("product_id", "nunique")
        )
        .reset_index()
    )

    # Join product information
    merged = holdings.merge(
        catalog[
            [
                "product_id",
                "product_name",
                "product_category"
            ]
        ],
        on="product_id",
        how="left"
    )

    # Number of unique product categories
    category_count = (
        merged.groupby("customer_id")
        ["product_category"]
        .nunique()
        .reset_index(
            name="product_categories_held"
        )
    )

    features = product_count.merge(
        category_count,
        on="customer_id",
        how="outer"
    )

    # Product category indicators
    category_flags = pd.crosstab(
        merged["customer_id"],
        merged["product_category"]
    )

    category_flags.columns = [
        "holding_" +
        str(col).lower().replace(" ", "_")
        for col in category_flags.columns
    ]

    category_flags = (
        category_flags
        .reset_index()
    )

    features = features.merge(
        category_flags,
        on="customer_id",
        how="left"
    )

    return features

def engineer_campaign_features(interactions):
    """
    Calculate customer-level campaign engagement metrics.
    """

    df = interactions.copy()

    grouped = (
        df.groupby("customer_id")
        .agg(
            campaigns_received=(
                "campaign_id",
                "count"
            ),
            campaigns_delivered=(
                "delivered",
                "sum"
            ),
            campaigns_opened=(
                "opened",
                "sum"
            ),
            campaigns_clicked=(
                "clicked",
                "sum"
            ),
            campaigns_converted=(
                "converted",
                "sum"
            ),
        )
        .reset_index()
    )

    grouped["campaign_open_rate"] = safe_divide(
        grouped["campaigns_opened"],
        grouped["campaigns_delivered"]
    )

    grouped["campaign_click_rate"] = safe_divide(
        grouped["campaigns_clicked"],
        grouped["campaigns_delivered"]
    )

    grouped["campaign_conversion_rate"] = safe_divide(
        grouped["campaigns_converted"],
        grouped["campaigns_delivered"]
    )

    grouped["engagement_score"] = (
        0.25 * grouped["campaign_open_rate"]
        + 0.35 * grouped["campaign_click_rate"]
        + 0.40 * grouped["campaign_conversion_rate"]
    )

    return grouped

def engineer_recommendation_features(recommendations):
    """
    Calculate customer-level recommendation performance.
    """

    df = recommendations.copy()

    grouped = (
        df.groupby("customer_id")
        .agg(
            recommendations_received=(
                "recommendation_id",
                "count"
            ),
            average_suitability_score=(
                "suitability_score",
                "mean"
            ),
            recommendations_accepted=(
                "accepted",
                "sum"
            ),
            recommendations_converted=(
                "converted",
                "sum"
            ),
        )
        .reset_index()
    )

    grouped["recommendation_acceptance_rate"] = safe_divide(
        grouped["recommendations_accepted"],
        grouped["recommendations_received"]
    )

    grouped["recommendation_conversion_rate"] = safe_divide(
        grouped["recommendations_converted"],
        grouped["recommendations_received"]
    )

    return grouped

def build_customer_360(
    customers,
    transactions,
    product_holdings,
    products,
    campaign_interactions,
    recommendations
):
    """
    Build the final customer-level feature table.
    """

    # ---------------------------------------------------------
    # CUSTOMER PROFILE
    # ---------------------------------------------------------

    customer_features = engineer_customer_features(
        customers
    )

    # ---------------------------------------------------------
    # TRANSACTION FEATURES
    # ---------------------------------------------------------

    transaction_features = engineer_transaction_features(
        transactions
    )

    # ---------------------------------------------------------
    # PRODUCT FEATURES
    # ---------------------------------------------------------

    product_features = engineer_product_features(
        product_holdings,
        products
    )

    # ---------------------------------------------------------
    # CAMPAIGN FEATURES
    # ---------------------------------------------------------

    campaign_features = engineer_campaign_features(
        campaign_interactions
    )

    # ---------------------------------------------------------
    # RECOMMENDATION FEATURES
    # ---------------------------------------------------------

    recommendation_features = (
        engineer_recommendation_features(
            recommendations
        )
    )

    # ---------------------------------------------------------
    # MERGE EVERYTHING
    # ---------------------------------------------------------

    result = customer_features.merge(
        transaction_features,
        on="customer_id",
        how="left"
    )

    result = result.merge(
        product_features,
        on="customer_id",
        how="left"
    )

    result = result.merge(
        campaign_features,
        on="customer_id",
        how="left"
    )

    result = result.merge(
        recommendation_features,
        on="customer_id",
        how="left"
    )

    # ---------------------------------------------------------
    # FILL MISSING BEHAVIORAL VALUES
    # ---------------------------------------------------------

    numeric_columns = result.select_dtypes(
        include=np.number
    ).columns

    result[numeric_columns] = (
        result[numeric_columns]
        .fillna(0)
    )

    # ---------------------------------------------------------
    # RFM SCORE
    # ---------------------------------------------------------

    result["recency_score"] = pd.qcut(
        result["recency_days"].rank(method="first"),
        5,
        labels=[5, 4, 3, 2, 1]
    ).astype(int)

    result["frequency_score"] = pd.qcut(
        result["transaction_count"].rank(method="first"),
        5,
        labels=[1, 2, 3, 4, 5]
    ).astype(int)

    result["monetary_score"] = pd.qcut(
        result["total_transaction_amount"].rank(method="first"),
        5,
        labels=[1, 2, 3, 4, 5]
    ).astype(int)

    result["rfm_score"] = (
        result["recency_score"]
        + result["frequency_score"]
        + result["monetary_score"]
    )

    # ---------------------------------------------------------
    # SORT
    # ---------------------------------------------------------

    result = result.sort_values(
        "customer_id"
    ).reset_index(drop=True)

    return result