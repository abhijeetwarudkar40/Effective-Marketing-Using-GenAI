"""Added Finora Compliance & Approval module based on MarketMind flow."""
import streamlit as st
import finora_db

FLAGGED = [
    "100% guaranteed approval", "guaranteed returns", "risk-free investment",
    "instant loan approval", "lowest interest rate guaranteed", "no risk",
    "guaranteed profit", "zero risk",
]

def compliance_report(campaign):
    text=f"{campaign.get('subject','')} {campaign.get('subject_line','')} {campaign.get('body','')}".lower()
    claims=[x for x in FLAGGED if x in text]
    issues=[f"Unsupported claim detected: '{x}'" for x in claims]
    if not campaign.get("product_name"):
        issues.append("Product is not linked to the campaign.")
    if not campaign.get("body"):
        issues.append("Campaign message is missing.")
    if not campaign.get("call_to_action",campaign.get("cta")):
        issues.append("Call-to-action is missing.")
    # PersonalizedMarketingAI's existing dataset does not store consent fields.
    if not st.session_state.get("finora_consent_confirmed",False):
        issues.append("Channel consent is not stored in the current dataset; human confirmation is required.")
    score=max(0,100-20*len(claims)-10*(len(issues)-len(claims)))
    status="Approved" if score>=80 and not issues else ("Needs Review" if score>=50 else "Rejected")
    return score,status,issues

def render_compliance():
    st.markdown("## Compliance & Approval")
    st.caption("Added MarketMind-style safety checks and human-in-the-loop approval.")
    campaign=st.session_state.get("generated_campaign")
    if not campaign:
        st.info("Generate a campaign in Campaign Studio first."); return

    with st.container(border=True):
        a,b,c=st.columns(3)
        a.write(f"**Customer**\n\n{st.session_state.get('generated_customer_id','—')}")
        b.write(f"**Segment**\n\n{campaign.get('primary_segment','—')}")
        c.write(f"**Product**\n\n{campaign.get('product_name','—')}")

    score,status,issues=compliance_report(campaign)
    a,b=st.columns(2)
    a.metric("Compliance Score",f"{score}/100")
    b.metric("Status",status)

    st.markdown("### Safety Checks")
    if issues:
        for issue in issues:
            st.warning(issue)
    else:
        st.success("No issues detected.")

    st.checkbox(
        "I confirm that the campaign's selected channel has valid customer consent.",
        key="finora_consent_confirmed",
    )

    score,status,issues=compliance_report(campaign)
    st.divider()
    cid=st.session_state.get("finora_campaign_id")

    x,y=st.columns(2)
    with x:
        if st.button("Send for Review",key="finora_send_review",width="stretch"):
            cid=cid or finora_db.save_campaign(campaign,"Needs Review",score)
            finora_db.update_status(cid,"Needs Review")
            finora_db.log_approval(cid,"Sent for Review")
            st.session_state["finora_campaign_id"]=cid
            st.success("Campaign sent for human review.")
    with y:
        if st.button(
            "Approve Campaign",
            key="finora_approve_campaign",
            type="primary",
            disabled=not st.session_state.get("finora_consent_confirmed",False),
            width="stretch",
        ):
            cid=cid or finora_db.save_campaign(campaign,"Approved",score)
            finora_db.update_status(cid,"Approved")
            finora_db.log_approval(cid,"Approved","Human-in-the-loop approval granted")
            st.session_state["finora_campaign_id"]=cid
            st.session_state["campaign_approved"]=True
            st.success("Campaign approved. Continue to Campaign Delivery.")
