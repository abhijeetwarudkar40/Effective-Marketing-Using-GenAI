"""Added Finora Analytics module based on MarketMind analytics dashboard."""
import streamlit as st, pandas as pd
import finora_db

def render_analytics():
    st.markdown("## Campaign Analytics")
    st.caption("Campaign, approval and delivery activity for the added Finora modules.")
    campaigns=finora_db.campaigns(); deliveries=finora_db.deliveries()
    a,b,c,d=st.columns(4)
    a.metric("Campaigns",len(campaigns))
    b.metric("Approved",sum(x["status"]=="Approved" for x in campaigns))
    c.metric("Messages Sent",sum(x["status"] in ("SENT","DRY_RUN_SIMULATED") for x in deliveries))
    d.metric("Delivery Records",len(deliveries))
    if campaigns:
        df=pd.DataFrame(campaigns)
        x,y=st.columns(2)
        with x:
            st.markdown("### Campaign Status")
            st.bar_chart(df["status"].value_counts())
        with y:
            if "segment" in df:
                st.markdown("### Campaigns by Segment")
                st.bar_chart(df["segment"].value_counts())
        st.markdown("### Campaign Log"); st.dataframe(df,width="stretch",hide_index=True)
    if deliveries:
        st.markdown("### Delivery Log"); st.dataframe(pd.DataFrame(deliveries),width="stretch",hide_index=True)
