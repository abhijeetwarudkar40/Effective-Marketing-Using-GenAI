import streamlit as st

from .data_loader import (
    load_customers,
    load_recommendations,
    load_campaign_content,
    load_ab_variants,
    load_campaign_analytics,
)
from .helpers import page_header, section_header, kpi_card, field_value, empty_state


def render_customer_360():
    page_header(
        "Customer 360°",
        "Unified customer profile, recommendations and campaign intelligence.",
    )

    customers = load_customers()
    recommendations = load_recommendations()
    campaigns = load_campaign_content()
    ab = load_ab_variants()
    analytics = load_campaign_analytics()

    if customers.empty:
        if campaigns.empty or "customer_id" not in campaigns.columns:
            empty_state("Customer data is not available.")
            return
        customers = campaigns[["customer_id"]].drop_duplicates()

    if "customer_id" not in customers.columns:
        st.error("customer_id is missing from customer data.")
        return

    customer_ids = sorted(customers["customer_id"].dropna().astype(str).unique().tolist())
    if not customer_ids:
        empty_state("No customers are available.")
        return

    selected = st.selectbox("Select Customer", customer_ids)
    customer_match = customers[customers["customer_id"].astype(str) == selected]
    if customer_match.empty:
        return
    customer = customer_match.iloc[0]

    section_header("Customer Profile")
    fields = [
        ("Customer ID", "customer_id"),
        ("Segment", "primary_segment"),
        ("Persona", "customer_persona"),
        ("Retention Risk", "retention_risk"),
        ("Cross-Sell Opportunity", "cross_sell_opportunity"),
        ("Targeting Priority", "genai_targeting_priority"),
    ]
    cols = st.columns(3)
    for i, (label, field) in enumerate(fields):
        with cols[i % 3]:
            kpi_card(label, field_value(customer, field))

    section_header("Product Recommendations")
    if not recommendations.empty and "customer_id" in recommendations.columns:
        recs = recommendations[recommendations["customer_id"].astype(str) == selected]
        if not recs.empty:
            cols = [
                c for c in [
                    "product_name", "recommendation_score",
                    "recommendation_confidence", "recommendation_reason",
                    "campaign_objective",
                ] if c in recs.columns
            ]
            st.dataframe(recs[cols], use_container_width=True, hide_index=True)
        else:
            st.info("No recommendations found for this customer.")
    else:
        st.info("Recommendation data is not available.")

    section_header("Personalized Campaign")
    if not campaigns.empty and "customer_id" in campaigns.columns:
        campaign = campaigns[campaigns["customer_id"].astype(str) == selected]
        if not campaign.empty:
            row = campaign.iloc[0]
            with st.container(border=True):
                st.markdown(f"### {field_value(row, 'subject')}")
                st.markdown(f"**{field_value(row, 'headline')}**")
                st.write(field_value(row, "campaign_body"))
                st.markdown(f"**CTA:** {field_value(row, 'cta')}")
        else:
            st.info("No personalized campaign found.")
    else:
        st.info("Campaign content is not available.")

    section_header("A/B Campaign Evaluation")
    if not analytics.empty and "customer_id" in analytics.columns:
        result = analytics[analytics["customer_id"].astype(str) == selected]
        if not result.empty:
            row = result.iloc[0]
            c1, c2, c3, c4 = st.columns(4)
            with c1: kpi_card("Winner", field_value(row, "winning_variant"))
            with c2: kpi_card("Strategy", field_value(row, "winning_strategy"))
            with c3: kpi_card("Confidence", field_value(row, "ab_confidence"))
            with c4: kpi_card("Score Difference", field_value(row, "score_difference"))
        else:
            st.info("No A/B analytics found for this customer.")
    else:
        st.info("A/B analytics are not available.")

    if not ab.empty and "customer_id" in ab.columns:
        variants = ab[ab["customer_id"].astype(str) == selected]
        if not variants.empty:
            row = variants.iloc[0]
            a, b = st.columns(2)
            with a:
                with st.container(border=True):
                    st.markdown("### Variant A · Benefit-Focused")
                    st.markdown(f"**{field_value(row, 'variant_a_subject')}**")
                    st.write(field_value(row, "variant_a_body"))
                    st.caption(field_value(row, "variant_a_cta"))
            with b:
                with st.container(border=True):
                    st.markdown("### Variant B · Action-Focused")
                    st.markdown(f"**{field_value(row, 'variant_b_subject')}**")
                    st.write(field_value(row, "variant_b_body"))
                    st.caption(field_value(row, "variant_b_cta"))
