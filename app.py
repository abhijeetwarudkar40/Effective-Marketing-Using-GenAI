import streamlit as st

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="Personalized Marketing AI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------
# OPTIONAL CSS
# ---------------------------------------------------------

def load_css():
    st.markdown(
        """
        <style>

        .main-title {
            font-size: 38px;
            font-weight: 700;
            color: #102a43;
            margin-bottom: 5px;
        }

        .section-title {
            font-size: 30px;
            font-weight: 700;
            color: #102a43;
            margin-top: 35px;
            margin-bottom: 8px;
        }

        .section-subtitle {
            font-size: 16px;
            color: #7b8794;
            margin-bottom: 25px;
        }

        .campaign-card {
            border: 1px solid #d9e2ec;
            border-radius: 12px;
            padding: 22px;
            margin-bottom: 18px;
            background: white;
        }

        .field-label {
            font-size: 15px;
            font-weight: 700;
            color: #102a43;
            margin-bottom: 8px;
        }

        .field-value {
            font-size: 17px;
            color: #243b53;
            line-height: 1.6;
        }

        .subject-box {
            background: #e8f1ff;
            padding: 16px 20px;
            border-radius: 10px;
            color: #0056b3;
            font-size: 18px;
        }

        .message-box {
            border: 1px solid #d9e2ec;
            border-radius: 10px;
            padding: 18px;
            font-size: 17px;
            color: #243b53;
            line-height: 1.7;
            background: #ffffff;
        }

        .cta-box {
            display: inline-block;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            padding: 10px 18px;
            color: #486581;
            background: #ffffff;
            font-weight: 600;
        }

        .context-card {
            border: 1px solid #d9e2ec;
            border-radius: 10px;
            padding: 20px;
            min-height: 150px;
            background: #ffffff;
        }

        .success-box {
            background: #e8f8ee;
            border-radius: 10px;
            padding: 16px 20px;
            color: #087f5b;
            font-size: 17px;
            margin: 20px 0;
        }

        .warning-box {
            background: #fff9db;
            border-radius: 10px;
            padding: 16px 20px;
            color: #8d6b00;
            font-size: 17px;
            margin: 20px 0;
        }

        .variant-header {
            font-size: 22px;
            font-weight: 700;
            color: #102a43;
            margin-bottom: 15px;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


load_css()


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

st.sidebar.title("Personalized Marketing AI")

st.sidebar.caption(
    "Customer intelligence • Recommendations • GenAI campaigns"
)

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Customer 360°",
        "Segmentation",
        "Recommendations",
        "Campaign Studio",
        "Creative Studio",
        "Compliance & Approval",
        "Campaign Delivery",
        "Analytics",
    ],
)


# ---------------------------------------------------------
# SAFE IMPORTS FOR EXISTING UI MODULES
# ---------------------------------------------------------

if page == "Dashboard":

    try:
        from ui.dashboard import render_dashboard
        render_dashboard()
    except Exception as e:
        st.error("Dashboard could not be loaded.")
        st.exception(e)


elif page == "Customer 360°":

    try:
        from ui.customer_360 import render_customer_360
        render_customer_360()
    except Exception as e:
        st.error("Customer 360° could not be loaded.")
        st.exception(e)


elif page == "Segmentation":

    try:
        from ui.segmentation import render_segmentation
        render_segmentation()
    except Exception as e:
        st.error("Segmentation could not be loaded.")
        st.exception(e)


elif page == "Recommendations":

    try:
        from ui.recommendations import render_recommendations
        render_recommendations()
    except Exception as e:
        st.error("Recommendations could not be loaded.")
        st.exception(e)


elif page == "Campaign Studio":

    # -----------------------------------------------------
    # CAMPAIGN STUDIO
    # -----------------------------------------------------

    try:
        from ui.campaign_studio import render_campaign_studio
        render_campaign_studio()

    except Exception as e:

        st.title("Campaign Studio")

        st.error(
            "Campaign Studio could not be loaded from "
            "`ui.campaign_studio`."
        )

        st.exception(e)

elif page == "Creative Studio":

    try:
        from ui.creative_studio import render_creative_studio
        render_creative_studio()
    except Exception as e:
        st.title("Creative Studio")
        st.error("Creative Studio could not be loaded.")
        st.exception(e)


elif page == "Compliance & Approval":

    try:
        from ui.compliance_approval import render_compliance
        render_compliance()
    except Exception as e:
        st.title("Compliance & Approval")
        st.error("Compliance module could not be loaded.")
        st.exception(e)


elif page == "Campaign Delivery":

    try:
        from ui.campaign_delivery import render_delivery
        render_delivery()
    except Exception as e:
        st.title("Campaign Delivery")
        st.error("Campaign Delivery could not be loaded.")
        st.exception(e)


elif page == "Analytics":

    try:
        from ui.analytics import render_analytics
        render_analytics()
    except Exception as e:
        st.title("Analytics")
        st.error("Analytics module could not be loaded.")
        st.exception(e)
