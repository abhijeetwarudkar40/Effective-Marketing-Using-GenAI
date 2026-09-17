import pandas as pd
import streamlit as st

from .data_loader import (
    load_customers,
    load_recommendations,
    load_campaign_content,
    load_ab_variants,
    load_campaign_analytics,
)
from .helpers import page_header, section_header, kpi_card


def render_dashboard():
    page_header(
        "Marketing Intelligence Dashboard",
        "Overview of customers, recommendations, campaigns and model-based A/B evaluation.",
    )

    customers = load_customers()
    recommendations = load_recommendations()
    campaigns = load_campaign_content()
    ab = load_ab_variants()
    analytics = load_campaign_analytics()

    section_header("Platform Overview")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Customers", f"{customers['customer_id'].nunique():,}" if "customer_id" in customers.columns else 0)
    with c2:
        kpi_card("Recommendations", f"{len(recommendations):,}")
    with c3:
        kpi_card("Campaigns", f"{len(campaigns):,}")
    with c4:
        kpi_card("A/B Campaigns", f"{len(ab):,}")

    section_header(
        "A/B Campaign Evaluation",
        "Model-based evaluation. Actual opens, clicks and conversions are not available yet.",
    )

    if analytics.empty:
        st.info("campaign_analytics.csv is not available. Run Phase 5E first.")
        return

    a_wins = int((analytics.get("winning_variant", pd.Series(dtype=str)) == "A").sum())
    b_wins = int((analytics.get("winning_variant", pd.Series(dtype=str)) == "B").sum())
    ties = int((analytics.get("winning_variant", pd.Series(dtype=str)) == "Tie").sum())

    winning_variant = "A" if a_wins > b_wins else "B" if b_wins > a_wins else "Tie"
    if "winning_strategy" in analytics.columns and not analytics["winning_strategy"].empty:
        winning_strategy = analytics["winning_strategy"].value_counts().index[0]
    else:
        winning_strategy = "N/A"

    avg_a = float(pd.to_numeric(analytics.get("variant_a_score", 0), errors="coerce").fillna(0).mean())
    avg_b = float(pd.to_numeric(analytics.get("variant_b_score", 0), errors="coerce").fillna(0).mean())
    gap = abs(avg_a - avg_b)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Winning Variant", winning_variant, "Overall model winner")
    with c2:
        kpi_card("Winning Strategy", winning_strategy, "Best-performing model strategy")
    with c3:
        confidence = analytics["ab_confidence"].value_counts().index[0] if "ab_confidence" in analytics.columns and not analytics["ab_confidence"].empty else "N/A"
        kpi_card("A/B Confidence", confidence)
    with c4:
        kpi_card("Score Difference", f"{gap:.2f}", "Average model score gap")

    performance = pd.DataFrame({
        "Variant": ["A", "B", "Tie"],
        "Strategy": ["Benefit-Focused", "Action-Focused", "Equal"],
        "Average Score": [round(avg_a, 2), round(avg_b, 2), None],
        "Wins": [a_wins, b_wins, ties],
    })
    total = max(len(analytics), 1)
    performance["Win Rate %"] = (performance["Wins"] / total * 100).round(2)

    st.dataframe(performance, use_container_width=True, hide_index=True)

    if "campaign_objective" in analytics.columns:
        section_header("Campaign Objectives")
        objective = (
            analytics["campaign_objective"]
            .value_counts()
            .rename_axis("Objective")
            .reset_index(name="Campaigns")
        )
        st.dataframe(objective, use_container_width=True, hide_index=True)

    if "product_name" in analytics.columns:
        section_header("Campaign Products")
        product = (
            analytics["product_name"]
            .value_counts()
            .rename_axis("Product")
            .reset_index(name="Campaigns")
        )
        st.dataframe(product, use_container_width=True, hide_index=True)

    st.caption(
        "A/B performance is currently model-based because actual customer engagement data "
        "(opens, clicks and conversions) is not available."
    )
