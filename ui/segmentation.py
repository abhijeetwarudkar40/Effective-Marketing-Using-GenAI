import streamlit as st

from .data_loader import load_customers, load_segments, ensure_segments
from .helpers import page_header, section_header, kpi_card, empty_state


def render_segmentation():
    page_header(
        "Customer Segmentation",
        "Customer personas, retention risk and targeting priorities.",
    )

    customers = load_customers()
    segments = load_segments()
    if segments.empty:
        segments = ensure_segments(customers)

    if segments.empty:
        empty_state("Segmentation data is not available.")
        return

    customer_count = segments["customer_id"].nunique() if "customer_id" in segments.columns else len(segments)
    segment_count = segments["primary_segment"].nunique() if "primary_segment" in segments.columns else 0
    persona_count = segments["customer_persona"].nunique() if "customer_persona" in segments.columns else 0

    c1, c2, c3 = st.columns(3)
    with c1: kpi_card("Customers", f"{customer_count:,}")
    with c2: kpi_card("Segments", f"{segment_count:,}")
    with c3: kpi_card("Personas", f"{persona_count:,}")

    if "primary_segment" in segments.columns:
        section_header("Segment Distribution")
        st.bar_chart(segments["primary_segment"].value_counts())

    if "customer_persona" in segments.columns:
        section_header("Customer Personas")
        st.bar_chart(segments["customer_persona"].value_counts())

    if "retention_risk" in segments.columns:
        section_header("Retention Risk")
        st.bar_chart(segments["retention_risk"].value_counts())

    if "genai_targeting_priority" in segments.columns:
        section_header("GenAI Targeting Priority")
        st.bar_chart(segments["genai_targeting_priority"].value_counts())

    section_header("Customer Segmentation Detail")
    columns = [
        c for c in [
            "customer_id", "primary_segment", "customer_persona",
            "retention_risk", "cross_sell_opportunity",
            "genai_targeting_priority",
        ] if c in segments.columns
    ]
    st.dataframe(segments[columns], use_container_width=True, hide_index=True)
