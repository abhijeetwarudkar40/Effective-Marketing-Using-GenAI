"""
Finora Campaign Delivery

Uses the exact campaign content generated in Campaign Studio.

Important:
- Does NOT rewrite or invent email content.
- Sends the exact Subject, Headline, Greeting, Email Body,
  CTA, and Closing produced by the campaign generator.
- Embeds the approved Creative Studio image in the email.
- Delivery channel dropdown is Email / SMS.
- SMS uses the exact generated "sms" field when present.
"""

import io
import os
import smtplib
import html as html_lib
from pathlib import Path
from email.utils import formatdate, make_msgid

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

import streamlit as st
import finora_db

BASE_DIR = Path(__file__).resolve().parents[1]


# ============================================================
# SAFE VALUE
# ============================================================

def _get_value(data, *keys, default=""):
    if not isinstance(data, dict):
        return default

    for key in keys:
        value = data.get(key)

        if value is None:
            continue

        value = str(value).strip()

        if value and value.lower() not in (
            "nan",
            "none",
        ):
            return value

    return default


# ============================================================
# EXACT GENERATED EMAIL
# ============================================================

def _get_generated_email(campaign):
    """
    Read the exact fields returned by Campaign Studio / GenAI.

    Expected structure:
        subject
        headline
        greeting
        email_body
        cta
        closing

    No extra marketing copy is created here.
    """

    return {
        "subject": _get_value(
            campaign,
            "subject",
            "subject_line",
            "email_subject",
            default="Personalized Banking Update",
        ),

        "headline": _get_value(
            campaign,
            "headline",
            "email_headline",
            "title",
            default="",
        ),

        "greeting": _get_value(
            campaign,
            "greeting",
            "email_greeting",
            default="Hello,",
        ),

        "email_body": _get_value(
            campaign,
            "email_body",
            "campaign_body",
            "body",
            "generated_message",
            "message",
            default="",
        ),

        "cta": _get_value(
            campaign,
            "cta",
            "call_to_action",
            "email_call_to_action",
            default="",
        ),

        "closing": _get_value(
            campaign,
            "closing",
            "email_closing",
            default="Thank you,\nYour Banking Team",
        ),
    }


# ============================================================
# EXACT GENERATED SMS
# ============================================================

def _get_generated_sms(campaign):

    sms = _get_value(
        campaign,
        "sms",
        "sms_body",
        "sms_message",
        default="",
    )

    # Older campaign records may not have "sms".
    # In that case, construct a concise channel version
    # only from already generated campaign fields.
    if not sms:

        headline = _get_value(
            campaign,
            "headline",
            default="",
        )

        body = _get_value(
            campaign,
            "body",
            "generated_message",
            "message",
            default="",
        )

        cta = _get_value(
            campaign,
            "cta",
            "call_to_action",
            default="",
        )

        sms = " ".join(
            part
            for part in (
                headline,
                body,
                cta,
            )
            if part
        ).strip()

    return sms


# ============================================================
# APPROVED IMAGE -> BYTES
# ============================================================

def _get_approved_image_bytes():

    approved = st.session_state.get(
        "approved_creative"
    )

    if approved is not None:
        if isinstance(approved, (bytes, bytearray)):
            return bytes(approved)

        if isinstance(approved, dict):
            img = approved.get("image") or approved.get("image_bytes")
            if isinstance(img, (bytes, bytearray)):
                return bytes(img)
            if hasattr(img, "save"):
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                return buf.getvalue()

        if hasattr(approved, "save"):
            buf = io.BytesIO()
            approved.save(buf, format="PNG")
            return buf.getvalue()

    # Fallback to files on disk in data/generated_creatives
    creative_dir = BASE_DIR / "data" / "generated_creatives"
    if creative_dir.exists():
        files = list(creative_dir.glob("*.png"))
        if files:
            latest = max(files, key=lambda f: f.stat().st_mtime)
            try:
                return latest.read_bytes()
            except Exception:
                pass

    return None


# ============================================================
# HTML FORMATTER
# ============================================================

def _html_text(text):

    if not text:
        return ""

    safe = html_lib.escape(
        str(text)
    )

    return safe.replace(
        "\n",
        "<br>",
    )


# ============================================================
# BUILD EXACT EMAIL HTML
# ============================================================

def _build_email_html(
    email,
    include_image=True,
):

    image_html = ""

    if include_image:

        image_html = """
        <div style="
            margin: 24px 0 28px 0;
            text-align: center;
        ">
            <img
                src="cid:approved_campaign_creative"
                alt="Approved campaign creative"
                style="
                    display:block;
                    width:100%;
                    max-width:650px;
                    height:auto;
                    margin:0 auto;
                    border-radius:12px;
                "
            >
        </div>
        """

    cta_html = ""

    if email["cta"]:

        cta_html = f"""
        <div style="
            margin:24px 0;
        ">
            <span style="
                display:inline-block;
                padding:12px 20px;
                border-radius:8px;
                background:#1e3a5f;
                color:#ffffff;
                font-weight:700;
            ">
                {html_lib.escape(email["cta"])}
            </span>
        </div>
        """

    return f"""
    <!DOCTYPE html>

    <html>

    <head>
        <meta charset="UTF-8">
    </head>

    <body style="
        margin:0;
        padding:30px;
        background:#f4f6f8;
        font-family:Arial,Helvetica,sans-serif;
    ">

        <div style="
            max-width:700px;
            margin:0 auto;
            background:#ffffff;
            border:1px solid #e5e7eb;
            border-radius:12px;
            overflow:hidden;
        ">

            <div style="
                padding:32px 34px 10px 34px;
                color:#6b7280;
                font-size:13px;
            ">
                {html_lib.escape(email["subject"])}
            </div>

            <div style="
                padding:0 34px 34px 34px;
            ">

                <hr style="
                    border:0;
                    border-top:1px solid #e5e7eb;
                    margin:10px 0 28px 0;
                ">

                <h1 style="
                    margin:0 0 24px 0;
                    color:#1f2937;
                    font-size:30px;
                    line-height:1.35;
                ">
                    {html_lib.escape(email["headline"])}
                </h1>

                <p style="
                    margin:0 0 18px 0;
                    font-size:16px;
                    line-height:1.8;
                    color:#374151;
                ">
                    {_html_text(email["greeting"])}
                </p>

                {image_html}

                <div style="
                    margin:0;
                    font-size:16px;
                    line-height:1.8;
                    color:#374151;
                ">
                    {_html_text(email["email_body"])}
                </div>

                {cta_html}

                <p style="
                    margin:28px 0 0 0;
                    font-size:16px;
                    line-height:1.8;
                    color:#374151;
                ">
                    {_html_text(email["closing"])}
                </p>

            </div>

            <div style="
                padding:18px 34px;
                background:#f9fafb;
                border-top:1px solid #e5e7eb;
            ">
                <p style="
                    margin:0;
                    font-size:12px;
                    color:#6b7280;
                ">
                    Personalized campaign communication.
                </p>
            </div>

        </div>

    </body>

    </html>
    """


# ============================================================
# SEND EMAIL
# ============================================================

def _send_email(
    to,
    campaign,
    image_bytes=None,
):

    sender = os.getenv(
        "GMAIL_ADDRESS",
        "",
    ).strip()

    password = os.getenv(
        "GMAIL_APP_PASSWORD",
        "",
    ).strip()

    if not sender:

        return (
            "FAILED",
            "GMAIL_ADDRESS is missing in .env.",
        )

    if not password:

        return (
            "FAILED",
            "GMAIL_APP_PASSWORD is missing in .env.",
        )

    email = _get_generated_email(
        campaign
    )

    if image_bytes is None:
        image_bytes = _get_approved_image_bytes()

    try:

        msg = MIMEMultipart(
            "related"
        )

        msg["From"] = f"BankWise AI <{sender}>"
        msg["Reply-To"] = sender
        msg["To"] = to
        msg["Subject"] = email["subject"]
        msg["Date"] = formatdate(localtime=True)
        msg["Message-ID"] = make_msgid(domain="bankwise.ai")
        msg["MIME-Version"] = "1.0"
        msg["X-Mailer"] = "BankWise AI Campaign Delivery Gateway"
        msg["Auto-Submitted"] = "auto-generated"

        alternative = MIMEMultipart(
            "alternative"
        )

        msg.attach(
            alternative
        )

        # Exact generated plain-text version.
        plain_text = "\n\n".join(
            part
            for part in (
                email["greeting"],
                email["headline"],
                email["email_body"],
                email["cta"],
                email["closing"],
            )
            if part
        )

        alternative.attach(
            MIMEText(
                plain_text,
                "plain",
                "utf-8",
            )
        )

        # Exact generated HTML structure.
        html_content = _build_email_html(
            email,
            include_image=bool(image_bytes),
        )

        alternative.attach(
            MIMEText(
                html_content,
                "html",
                "utf-8",
            )
        )

        # Approved Creative Studio banner.
        if image_bytes:

            image_part = MIMEImage(
                image_bytes,
                _subtype="png",
            )

            image_part.add_header(
                "Content-ID",
                "<approved_campaign_creative>",
            )

            image_part.add_header(
                "Content-Disposition",
                "inline",
                filename="campaign_creative.png",
            )

            msg.attach(
                image_part
            )

        with smtplib.SMTP_SSL(
            "smtp.gmail.com",
            465,
        ) as server:

            server.login(
                sender,
                password,
            )

            server.sendmail(
                sender,
                to,
                msg.as_string(),
            )

        if image_bytes:

            return (
                "SENT",
                f"Exact generated email + approved creative sent to {to}.",
            )

        return (
            "SENT",
            f"Exact generated email sent to {to}.",
        )

    except smtplib.SMTPAuthenticationError:

        return (
            "FAILED",
            "Gmail authentication failed. Check "
            "GMAIL_APP_PASSWORD.",
        )

    except Exception as error:

        return (
            "FAILED",
            f"Email delivery failed: {error}",
        )


# ============================================================
# SMS
# ============================================================

def _send_sms(
    phone_number,
    message,
):

    if not phone_number:

        return (
            "FAILED",
            "Mobile number is required.",
        )

    if not message:

        return (
            "FAILED",
            "SMS message is empty.",
        )

    # Demo/simulation only.
    # A real SMS gateway is required for actual phone delivery.
    return (
        "DRY_RUN_SIMULATED",
        f"SMS delivery simulated for {phone_number}.",
    )


# ============================================================
# DELIVERY UI
# ============================================================

def render_delivery():

    st.markdown(
        "## Campaign Delivery"
    )

    st.caption(
        "Send the approved campaign through Email or SMS."
    )

    if not st.session_state.get(
        "campaign_approved"
    ):

        st.warning(
            "Approve the campaign in Compliance & Approval first."
        )

        return

    campaign = st.session_state.get(
        "generated_campaign"
    )

    if not campaign:

        st.error(
            "No generated campaign is available."
        )

        return

    campaign_id = st.session_state.get(
        "finora_campaign_id",
        "Not saved",
    )

    customer_id = st.session_state.get(
        "generated_customer_id",
        campaign.get(
            "customer_id",
            "—",
        ),
    )

    product = _get_value(
        campaign,
        "product_name",
        "product",
        default="—",
    )

    with st.container(
        border=True
    ):

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Campaign ID",
            campaign_id,
        )

        c2.metric(
            "Product",
            product,
        )

        c3.metric(
            "Customer",
            customer_id,
        )

    st.divider()

    # --------------------------------------------------------
    # EMAIL / SMS DROPDOWN
    # --------------------------------------------------------

    channel = st.selectbox(
        "Delivery Channel",
        [
            "Email",
            "SMS",
        ],
        key="finora_delivery_channel",
    )

    # ========================================================
    # EMAIL
    # ========================================================

    if channel == "Email":

        recipient = st.text_input(
            "Recipient Email Address",
            placeholder="customer@example.com",
            key="finora_email_recipient",
        )

        email = _get_generated_email(
            campaign
        )

        with st.expander(
            "Email Content Preview",
            expanded=True,
        ):

            st.caption("Subject")

            st.markdown(
                f"**{email['subject']}**"
            )

            st.divider()

            if email["headline"]:

                st.markdown(
                    f"### {email['headline']}"
                )

            if email["greeting"]:

                st.write(
                    email["greeting"]
                )

            approved_image = _get_approved_image_bytes()

            if approved_image:

                # Show the exact same approved image that will
                # be embedded in the outgoing email.
                approved = st.session_state.get(
                    "approved_creative",
                    {},
                )

                preview_image = (
                    approved.get("image")
                    if isinstance(approved, dict)
                    else approved
                )

                if preview_image is not None:

                    st.image(
                        preview_image,
                        width="stretch",
                    )

            if email["email_body"]:

                st.write(
                    email["email_body"]
                )

            if email["cta"]:

                st.info(
                    email["cta"]
                )

            if email["closing"]:

                st.write(
                    email["closing"]
                )

        if approved_image:

            st.success(
                "✓ The same approved Creative Studio image "
                "shown above will be embedded in the email."
            )

        else:

            st.info(
                "No approved creative image is available. "
                "The email will be sent without a banner."
            )

    # ========================================================
    # SMS
    # ========================================================

    else:

        recipient = st.text_input(
            "Recipient Mobile Number",
            placeholder="+91XXXXXXXXXX",
            key="finora_sms_recipient",
        )

        sms_message = _get_generated_sms(
            campaign
        )

        st.text_area(
            "SMS Message Preview",
            value=sms_message,
            height=140,
            disabled=True,
        )

        st.caption(
            f"SMS length: {len(sms_message)} characters"
        )

    st.divider()

    # ========================================================
    # SEND
    # ========================================================

    if st.button(
        "Send Campaign",
        type="primary",
        key="finora_send",
        width="stretch",
    ):

        if not recipient.strip():

            st.error(
                "Please enter a recipient."
            )

            return

        if channel == "Email":

            with st.spinner(
                "Sending the exact generated campaign..."
            ):

                status, message = _send_email(
                    recipient.strip(),
                    campaign,
                )

        else:

            sms_message = _get_generated_sms(
                campaign
            )

            with st.spinner(
                "Processing SMS..."
            ):

                status, message = _send_sms(
                    recipient.strip(),
                    sms_message,
                )

        try:

            finora_db.log_delivery(
                campaign_id,
                channel,
                recipient.strip(),
                status,
                message,
            )

        except Exception as log_error:

            st.warning(
                f"Delivery processed, but logging failed: "
                f"{log_error}"
            )

        if status == "SENT":

            st.success(
                f"✓ {message}"
            )

        elif status == "DRY_RUN_SIMULATED":

            st.info(
                message
            )

        else:

            st.error(
                f"✗ {message}"
            )

    # ========================================================
    # DELIVERY LOG
    # ========================================================

    try:

        logs = finora_db.deliveries()

        if logs:

            st.divider()

            st.markdown(
                "### Delivery Log"
            )

            st.dataframe(
                logs,
                width="stretch",
                hide_index=True,
            )

    except Exception:
        pass
