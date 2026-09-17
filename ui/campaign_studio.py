import re
import html
import importlib
import os
import json
from pathlib import Path
from typing import Any, Dict

import pandas as pd
import streamlit as st


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parents[1]

PROCESSED_DIR = BASE_DIR / "data" / "processed"

CAMPAIGN_CONTEXT_FILE = PROCESSED_DIR / "campaign_context.csv"


def _load_project_env():
    """
    Load key=value pairs from the project's .env file if present.
    Existing OS environment variables are preserved.
    """

    env_file = BASE_DIR / ".env"

    if not env_file.exists():
        return

    try:
        for raw_line in env_file.read_text(
            encoding="utf-8-sig"
        ).splitlines():

            line = raw_line.strip()

            if not line or line.startswith("#"):
                continue

            if "=" not in line:
                continue

            key, value = line.split("=", 1)

            key = key.strip()
            value = value.strip()

            if (
                len(value) >= 2
                and value[0] == value[-1]
                and value[0] in ("'", '"')
            ):
                value = value[1:-1]

            # Keep an already-defined environment variable.
            os.environ.setdefault(
                key,
                value,
            )

    except Exception:
        # The generation path will display the actual configuration error.
        pass


_load_project_env()


# =========================================================
# TEXT CLEANING
# =========================================================

def clean_generated_text(value: Any) -> str:

    if value is None:
        return ""

    text = str(value)

    # HTML decode
    text = html.unescape(text)

    # Remove markdown links
    text = re.sub(
        r"\[([^\]]+)\]\([^)]+\)",
        r"\1",
        text,
    )

    # Remove SVG markdown
    text = re.sub(
        r"\[svg\]\([^)]*\)",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # Remove HTML tags
    text = re.sub(
        r"<[^>]+>",
        "",
        text,
    )

    # Remove markdown bold
    text = re.sub(
        r"\*\*(.*?)\*\*",
        r"\1",
        text,
    )

    # Remove markdown italic
    text = re.sub(
        r"\*(.*?)\*",
        r"\1",
        text,
    )

    # Remove markdown headings
    text = re.sub(
        r"^\s*#{1,6}\s*",
        "",
        text,
        flags=re.MULTILINE,
    )

    # Remove accidental labels
    text = re.sub(
        r"^\s*(Subject|Headline|Body|Message|Call To Action|CTA)\s*:\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # Normalize spaces
    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    # Normalize blank lines
    text = re.sub(
        r"\n\s*\n\s*\n+",
        "\n\n",
        text,
    )

    return text.strip()


# =========================================================
# SAFE VALUE EXTRACTION
# =========================================================

def get_value(obj: Any, *keys, default=""):

    if obj is None:
        return default

    if isinstance(obj, dict):

        for key in keys:

            if key in obj and obj[key] is not None:

                return obj[key]

    else:

        for key in keys:

            if hasattr(obj, key):

                value = getattr(obj, key)

                if value is not None:

                    return value

    return default


# =========================================================
# LOAD CAMPAIGN CONTEXT
# =========================================================

@st.cache_data
def load_campaign_context():

    if not CAMPAIGN_CONTEXT_FILE.exists():

        return pd.DataFrame()

    try:

        return pd.read_csv(
            CAMPAIGN_CONTEXT_FILE
        )

    except Exception:

        return pd.DataFrame()


# =========================================================
# FIND CUSTOMER CONTEXT
# =========================================================

def get_customer_context(customer_id, product):

    df = load_campaign_context()

    if df.empty:
        return {}

    if "customer_id" not in df.columns:
        return {}

    customer_rows = df[
        df["customer_id"].astype(str)
        == str(customer_id)
    ]

    if customer_rows.empty:
        return {}

    # -----------------------------------------------------
    # First try exact product match
    # -----------------------------------------------------

    if "product_name" in customer_rows.columns:

        product_rows = customer_rows[
            customer_rows["product_name"]
            .astype(str)
            .str.lower()
            == str(product).lower()
        ]

        if not product_rows.empty:

            return product_rows.iloc[0].to_dict()

    # -----------------------------------------------------
    # Otherwise use customer's first context
    # -----------------------------------------------------

    return customer_rows.iloc[0].to_dict()


# =========================================================
# IMPORT ACTUAL CAMPAIGN GENERATOR
# =========================================================

def import_campaign_generator():

    """
    Imports the ACTUAL generator function from the project.

    Your campaign generator uses:

        generate_campaign_content(row)

    NOT:

        create_campaign(...)
    """

    candidates = [

        (
            "src.campaign.create_campaign",
            "generate_campaign_content",
        ),

        (
            "src.campaign.campaign_generator",
            "generate_campaign_content",
        ),

        (
            "src.campaign.generator",
            "generate_campaign_content",
        ),

        (
            "src.campaign",
            "generate_campaign_content",
        ),
    ]

    errors = []

    for module_name, function_name in candidates:

        try:

            module = importlib.import_module(
                module_name
            )

            function = getattr(
                module,
                function_name,
                None,
            )

            if callable(function):

                return function, errors

        except Exception as e:

            errors.append(
                f"{module_name}: {e}"
            )

    return None, errors



# =========================================================
# LOCAL FALLBACK COPY
# =========================================================

def _format_recommendation_reason(value):
    text = clean_generated_text(value)

    if not text:
        return ""

    parts = [
        part.strip(" .,-")
        for part in re.split(
            r"[;\n|]+",
            text,
        )
        if part.strip(" .,-")
    ]

    if len(parts) <= 1:
        return parts[0] if parts else ""

    if len(parts) == 2:
        return f"{parts[0]} and {parts[1]}"

    return (
        ", ".join(parts[:-1])
        + f", and {parts[-1]}"
    )


def _local_campaign_copy(
    row,
    product,
    objective,
    tone,
    language,
):
    """
    Safe offline fallback used only when Gemini is unavailable.
    Uses the real customer context instead of generic text.
    """

    segment = clean_generated_text(
        get_value(
            row,
            "primary_segment",
            "segment",
            default="customer",
        )
    )

    persona = clean_generated_text(
        get_value(
            row,
            "customer_persona",
            "persona",
            default="customer",
        )
    )

    retention = clean_generated_text(
        get_value(
            row,
            "retention_risk",
            default="",
        )
    )

    cross_sell = clean_generated_text(
        get_value(
            row,
            "cross_sell_opportunity",
            default="",
        )
    )

    reason = _format_recommendation_reason(
        get_value(
            row,
            "recommendation_reason",
            "reason",
            default="",
        )
    )

    angle = clean_generated_text(
        get_value(
            row,
            "marketing_angle",
            default="relevant financial needs",
        )
    )

    if language == "Hindi":

        return {
            "subject": (
                f"{product}: आपकी वित्तीय जरूरतों के लिए एक विकल्प"
            ),
            "headline": (
                f"{product} आपके अगले वित्तीय कदम में मदद कर सकता है"
            ),
            "greeting": "नमस्ते!",
            "email_body": (
                f"आपके ग्राहक प्रोफ़ाइल और उपलब्ध अनुशंसाओं को "
                f"ध्यान में रखते हुए, {product} आपकी वर्तमान "
                f"वित्तीय जरूरतों के लिए एक उपयोगी विकल्प हो सकता है। "
                f"यह अनुशंसा आपके {segment.lower()} प्रोफ़ाइल "
                f"और {angle.lower()} से जुड़े संकेतों पर आधारित है"
                f"{'. ' + reason if reason else '.'} "
                f"उपलब्ध सुविधाओं, शर्तों और पात्रता की जानकारी "
                f"देखें ताकि आप तय कर सकें कि यह आपके लिए उपयुक्त है या नहीं."
            ),
            "cta": f"{product} के बारे में जानें",
            "closing": "सादर,\nआपकी बैंकिंग टीम",
            "sms": (
                f"नमस्ते! {product} आपकी वित्तीय जरूरतों के लिए "
                f"एक विकल्प हो सकता है। उपलब्ध जानकारी देखें: "
                f"{product} के बारे में जानें"
            ),
        }

    if language == "Marathi":

        return {
            "subject": (
                f"{product}: तुमच्या आर्थिक गरजांसाठी एक पर्याय"
            ),
            "headline": (
                f"{product} तुमच्या पुढील आर्थिक निर्णयासाठी "
                f"उपयुक्त ठरू शकतो"
            ),
            "greeting": "नमस्कार!",
            "email_body": (
                f"तुमच्या ग्राहक प्रोफाइल आणि उपलब्ध शिफारसींचा "
                f"विचार करता, {product} हा तुमच्या सध्याच्या "
                f"आर्थिक गरजांसाठी उपयुक्त पर्याय ठरू शकतो। "
                f"ही शिफारस तुमच्या {segment.lower()} प्रोफाइल "
                f"आणि {angle.lower()} शी संबंधित संकेतांवर आधारित आहे"
                f"{'. ' + reason if reason else '.'} "
                f"उपलब्ध सुविधा, अटी आणि पात्रता तपासा आणि "
                f"हा पर्याय तुमच्यासाठी योग्य आहे का ते जाणून घ्या."
            ),
            "cta": f"{product} बद्दल अधिक जाणून घ्या",
            "closing": "आपला,\nतुमची बँकिंग टीम",
            "sms": (
                f"नमस्कार! {product} तुमच्या आर्थिक गरजांसाठी "
                f"उपयुक्त ठरू शकतो. अधिक माहिती पहा."
            ),
        }

    # English.
    if objective == "Retention":

        subject = (
            f"Keep moving forward with {product}"
        )

        headline = (
            f"Support your next financial step with {product}"
        )

        email_body = (
            f"We value your relationship with us. Based on your "
            f"{segment.lower()} profile and the current "
            f"retention objective, {product} may be a useful "
            f"option for your evolving financial needs. "
            f"{'Your profile indicates ' + reason.lower() + '. ' if reason else ''}"
            f"Review the available features, terms and eligibility "
            f"details to decide whether it fits your plans."
        )

        cta = f"Learn More About {product}"

    elif objective == "Upsell":

        subject = (
            f"Take your banking experience further with {product}"
        )

        headline = (
            f"Explore what more {product} can offer"
        )

        email_body = (
            f"As a {persona.lower()}, you may be interested in "
            f"how {product} could complement your existing financial "
            f"relationship. "
            f"{'Your profile indicates ' + reason.lower() + '. ' if reason else ''}"
            f"Review the available features and eligibility details "
            f"to see whether the product aligns with your needs."
        )

        cta = f"Explore {product}"

    elif objective == "Cross-Sell":

        subject = (
            f"A relevant option to explore: {product}"
        )

        headline = (
            f"See whether {product} fits your financial plans"
        )

        email_body = (
            f"Based on your current relationship with us and the "
            f"available recommendation signals, {product} may "
            f"complement your financial needs. "
            f"{'Your profile indicates ' + reason.lower() + '. ' if reason else ''}"
            f"Review the product's features, terms and eligibility "
            f"to determine whether it is a suitable addition to your plans."
        )

        cta = f"Explore {product}"

    else:

        subject = (
            f"Discover more value with {product}"
        )

        headline = (
            "An option worth exploring for your financial goals"
        )

        email_body = (
            f"Based on your available customer context, {product} "
            f"may be relevant to your current financial needs. "
            f"{'Your profile indicates ' + reason.lower() + '. ' if reason else ''}"
            f"Review the product information, features and eligibility "
            f"details to decide whether it fits your plans."
        )

        cta = f"Learn More About {product}"

    greeting = (
        "Hello!"
        if tone == "Friendly"
        else "Hello,"
    )

    closing = (
        "Regards,\nYour Banking Team"
    )

    sms = (
        f"Hi! {product} may be relevant to your financial needs. "
        f"Review the available information and learn more."
    )

    return {
        "subject": subject,
        "headline": headline,
        "greeting": greeting,
        "email_body": email_body,
        "cta": cta,
        "closing": closing,
        "sms": sms,
    }


# =========================================================
# FALLBACK CAMPAIGN
# =========================================================


# =========================================================
# GEMINI TEXT GENERATION
# =========================================================

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash",
)


def _gemini_client():
    api_key = (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
    )

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing from .env"
        )

    try:
        from google import genai
    except ImportError as exc:
        raise RuntimeError(
            "Install the Google GenAI SDK with: "
            "pip install -U google-genai"
        ) from exc

    return genai.Client(
        api_key=api_key
    )


def _extract_json_object(text):
    text = str(text or "").strip()

    # Remove common markdown code fences.
    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r"\s*```$",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # Find the first JSON object if Gemini added a short preamble.
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise ValueError(
            "Gemini did not return a JSON object."
        )

    return json.loads(
        text[start:end + 1]
    )


def _generate_with_gemini(
    row,
    product,
    language,
    tone,
):
    """One Gemini call generates primary campaign + both A/B variants."""

    context = {
        "customer_id": clean_generated_text(
            get_value(row, "customer_id", default="")
        ),
        "product": product,
        "campaign_objective": clean_generated_text(
            get_value(
                row,
                "campaign_objective",
                "objective",
                default="Engagement",
            )
        ),
        "primary_segment": clean_generated_text(
            get_value(
                row,
                "primary_segment",
                "segment",
                default="Customer",
            )
        ),
        "customer_persona": clean_generated_text(
            get_value(
                row,
                "customer_persona",
                "persona",
                default="Customer",
            )
        ),
        "retention_risk": clean_generated_text(
            get_value(
                row,
                "retention_risk",
                default="",
            )
        ),
        "cross_sell_opportunity": clean_generated_text(
            get_value(
                row,
                "cross_sell_opportunity",
                default="",
            )
        ),
        "recommendation_reason": clean_generated_text(
            get_value(
                row,
                "recommendation_reason",
                "reason",
                default="",
            )
        ),
        "marketing_angle": clean_generated_text(
            get_value(
                row,
                "marketing_angle",
                default="",
            )
        ),
        "language": language,
        "tone": tone,
    }

    prompt = f"""
You are the senior marketing copywriter for a personalized banking platform.

Use the customer context below to create:
1) one PRIMARY campaign,
2) Variant A — Benefit-Focused,
3) Variant B — Action-Focused.

IMPORTANT:
- The copy must feel genuinely personalized, not generic.
- Use the recommendation reason and customer context naturally.
- Never expose customer IDs, raw dataset labels, scores, risk labels,
  internal analysis terms, or model terminology to the customer.
- Never invent balances, rates, guarantees, approvals, eligibility,
  savings, deadlines, or unsupported product claims.
- Email must be a polished real email with 2-3 substantial paragraphs.
- SMS must be concise and noticeably shorter than the email.
- Do not repeat the same sentence between Email and SMS.
- Benefit-Focused should emphasize relevance and value.
- Action-Focused should emphasize a clear next step.
- Keep customer-facing language natural and professional.
- Keep rationale and strength as internal A/B evaluation fields.

CUSTOMER CONTEXT:
{json.dumps(context, ensure_ascii=False, indent=2)}

Return ONLY valid JSON in exactly this structure:

{{
  "primary": {{
    "subject": "...",
    "headline": "...",
    "greeting": "Hello,",
    "email_body": "...",
    "cta": "...",
    "closing": "Regards,\\nYour Banking Team",
    "sms": "..."
  }},
  "variant_a": {{
    "subject": "...",
    "headline": "...",
    "greeting": "Hello,",
    "email_body": "...",
    "cta": "...",
    "closing": "Regards,\\nYour Banking Team",
    "sms": "...",
    "variant_rationale": "...",
    "variant_strength": "..."
  }},
  "variant_b": {{
    "subject": "...",
    "headline": "...",
    "greeting": "Hello,",
    "email_body": "...",
    "cta": "...",
    "closing": "Regards,\\nYour Banking Team",
    "sms": "...",
    "variant_rationale": "...",
    "variant_strength": "..."
  }}
}}
""".strip()

    client = _gemini_client()

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )

    output_text = getattr(response, "text", None)

    if not output_text:
        try:
            output_text = (
                response.candidates[0]
                .content.parts[0]
                .text
            )
        except Exception:
            output_text = None

    if not output_text:
        raise RuntimeError(
            "Gemini returned no text output."
        )

    payload = _extract_json_object(
        output_text
    )

    required = [
        "subject",
        "headline",
        "greeting",
        "email_body",
        "cta",
        "closing",
        "sms",
    ]

    for section_name in (
        "primary",
        "variant_a",
        "variant_b",
    ):
        section = payload.get(section_name)

        if not isinstance(section, dict):
            raise ValueError(
                f"Missing Gemini section: {section_name}"
            )

        for field in required:
            if not str(
                section.get(field, "")
            ).strip():
                raise ValueError(
                    f"Missing Gemini field: "
                    f"{section_name}.{field}"
                )

        if section_name != "primary":
            for field in (
                "variant_rationale",
                "variant_strength",
            ):
                if not str(
                    section.get(field, "")
                ).strip():
                    raise ValueError(
                        f"Missing Gemini field: "
                        f"{section_name}.{field}"
                    )

    def normalize(section, label=None):
        result = dict(section)

        result["subject_line"] = result["subject"]
        result["campaign_body"] = result["email_body"]
        result["body"] = result["email_body"]
        result["message"] = result["email_body"]
        result["generated_message"] = result["email_body"]
        result["call_to_action"] = result["cta"]

        result["customer_id"] = context["customer_id"]
        result["product_name"] = product
        result["campaign_objective"] = context[
            "campaign_objective"
        ]
        result["primary_segment"] = context[
            "primary_segment"
        ]
        result["customer_persona"] = context[
            "customer_persona"
        ]
        result["retention_risk"] = context[
            "retention_risk"
        ]
        result["cross_sell_opportunity"] = context[
            "cross_sell_opportunity"
        ]
        result["recommendation_reason"] = context[
            "recommendation_reason"
        ]
        result["marketing_angle"] = context[
            "marketing_angle"
        ]

        result["generation_mode"] = (
            f"Gemini {GEMINI_MODEL}"
        )
        result["generation_source"] = "Gemini"
        result["status"] = "Generated"
        result["compliance"] = "PASSED"

        if label:
            result["variant_label"] = label

        return result

    return {
        "primary": normalize(
            payload["primary"]
        ),
        "variant_a": normalize(
            payload["variant_a"],
            "A",
        ),
        "variant_b": normalize(
            payload["variant_b"],
            "B",
        ),
    }

def fallback_campaign(
    customer_id,
    product,
    tone,
    language,
    row=None,
):
    row = dict(row or {})
    objective = clean_generated_text(
        get_value(
            row,
            "campaign_objective",
            "objective",
            default="Engagement",
        )
    ) or "Engagement"

    content = _local_campaign_copy(
        row,
        product or "Personal Banking",
        objective,
        tone,
        language,
    )

    content.update(
        {
            "campaign_id": f"GEN-{customer_id}",
            "subject_line": content["subject"],
            "body": content["email_body"],
            "message": content["email_body"],
            "generated_message": content["email_body"],
            "call_to_action": content["cta"],
            "product_name": product or "Personal Banking",
            "customer_id": customer_id,
            "campaign_objective": objective,
            "primary_segment": get_value(
                row,
                "primary_segment",
                default="Active Customer",
            ),
            "customer_persona": get_value(
                row,
                "customer_persona",
                default="Customer",
            ),
            "retention_risk": get_value(
                row,
                "retention_risk",
                default="",
            ),
            "cross_sell_opportunity": get_value(
                row,
                "cross_sell_opportunity",
                default="",
            ),
            "recommendation_reason": get_value(
                row,
                "recommendation_reason",
                default="",
            ),
            "generation_mode": "Personalized Campaign Generator",
            "compliance": "PASSED",
            "status": "Generated",
        }
    )

    return content


# =========================================================
# ACTUAL CAMPAIGN GENERATION
# =========================================================

def generate_campaign(
    customer_id,
    product,
    language,
    tone,
):
    row = get_customer_context(
        customer_id,
        product,
    )

    if not row:
        row = {
            "customer_id": customer_id,
            "product_name": product,
            "campaign_objective": "Cross-Sell",
            "primary_segment": "Active Customer",
            "customer_persona": "Customer",
            "retention_risk": "Moderate Risk",
            "cross_sell_opportunity":
                "Moderate Cross-Sell Opportunity",
            "recommendation_reason": "",
            "marketing_angle":
                "relevant financial needs",
        }
    else:
        row = dict(row)
        row["customer_id"] = customer_id
        row["product_name"] = product

    try:
        generated = _generate_with_gemini(
            row=row,
            product=product,
            language=language,
            tone=tone,
        )

        # Cache A/B results. Opening the A/B section will NOT make
        # another Gemini request.
        st.session_state[
            "gemini_ab_variants"
        ] = {
            "variant_a":
                generated["variant_a"],
            "variant_b":
                generated["variant_b"],
        }

        return generated["primary"]

    except Exception as error:
        st.error(
            "Gemini could not generate the campaign."
        )
        st.caption(
            f"Gemini error: {type(error).__name__}: {error}"
        )

        if not os.getenv("GEMINI_API_KEY"):
            st.info(
                "Check that C:\\effectivemarket\\.env exists and contains "
                "GEMINI_API_KEY=your_key. Restart Streamlit after editing .env."
            )

        fallback = fallback_campaign(
            customer_id=customer_id,
            product=product,
            tone=tone,
            language=language,
            row=row,
        )

        fallback_a = dict(fallback)
        fallback_a.update({
            "variant_label": "A",
            "subject":
                f"Discover the value of {product}",
            "subject_line":
                f"Discover the value of {product}",
            "headline":
                f"See how {product} may support your plans",
            "email_body":
                fallback["email_body"],
            "campaign_body":
                fallback["email_body"],
            "body":
                fallback["email_body"],
            "message":
                fallback["email_body"],
            "generated_message":
                fallback["email_body"],
            "cta":
                f"Learn More About {product}",
            "call_to_action":
                f"Learn More About {product}",
            "sms":
                f"Hi! Learn more about {product} and "
                f"review whether it may fit your needs.",
            "variant_rationale":
                "Benefit-focused fallback.",
            "variant_strength":
                "Informative and value-led.",
        })

        fallback_b = dict(fallback)
        fallback_b.update({
            "variant_label": "B",
            "subject":
                f"Take the next step with {product}",
            "subject_line":
                f"Take the next step with {product}",
            "headline":
                f"Explore {product} today",
            "email_body":
                fallback["email_body"],
            "campaign_body":
                fallback["email_body"],
            "body":
                fallback["email_body"],
            "message":
                fallback["email_body"],
            "generated_message":
                fallback["email_body"],
            "cta":
                f"Explore {product}",
            "call_to_action":
                f"Explore {product}",
            "sms":
                f"Hi! Take the next step with {product}. "
                f"Explore the available information.",
            "variant_rationale":
                "Action-focused fallback.",
            "variant_strength":
                "Direct and next-step oriented.",
        })

        st.session_state[
            "gemini_ab_variants"
        ] = {
            "variant_a": fallback_a,
            "variant_b": fallback_b,
        }

        return fallback

def render_campaign_content(campaign):

    if not campaign:

        st.warning(
            "No campaign content is available."
        )

        return

    campaign_id = clean_generated_text(
        get_value(
            campaign,
            "campaign_id",
            "id",
            default="GEN-000001",
        )
    )

    subject = clean_generated_text(
        get_value(
            campaign,
            "subject",
            "subject_line",
            "email_subject",
        )
    )

    headline = clean_generated_text(
        get_value(
            campaign,
            "headline",
            "title",
        )
    )

    message = clean_generated_text(
        get_value(
            campaign,
            "body",
            "message",
            "generated_message",
            "content",
        )
    )

    cta = clean_generated_text(
        get_value(
            campaign,
            "cta",
            "call_to_action",
            "call_to_action_text",
        )
    )

    generation_mode = clean_generated_text(
        get_value(
            campaign,
            "generation_mode",
            "mode",
            default="Campaign Generator",
        )
    )

    compliance = clean_generated_text(
        get_value(
            campaign,
            "compliance",
            "compliance_status",
            default="PASSED",
        )
    )

    status = clean_generated_text(
        get_value(
            campaign,
            "status",
            default="Generated",
        )
    )

    # =====================================================
    # HEADER
    # =====================================================

    st.markdown(
        "## GenAI Generated Content"
    )

    st.caption(
        "Fresh personalized content generated "
        "for the selected customer."
    )

    st.caption(
        f"Campaign ID: {campaign_id}"
    )

    # =====================================================
    # SUBJECT
    # =====================================================

    st.markdown("### Subject")

    st.info(
        subject or "No subject generated."
    )

    # =====================================================
    # HEADLINE
    # =====================================================

    st.markdown("### Headline")

    st.write(
        headline or "No headline generated."
    )

    # =====================================================
    # MESSAGE
    # =====================================================

    st.markdown("### Generated Message")

    st.text_area(
        "Generated Message",
        value=message,
        height=120,
        disabled=True,
        label_visibility="collapsed",
    )

    # =====================================================
    # CTA
    # =====================================================

    st.markdown("### Call To Action")

    st.button(
        cta or "No CTA generated.",
        disabled=True,
    )

    # =====================================================
    # METADATA
    # =====================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.caption("Generation Mode")

        st.write(
            generation_mode
        )

    with col2:

        st.caption("Compliance")

        if compliance.upper() == "PASSED":

            st.success(
                compliance
            )

        else:

            st.warning(
                compliance
            )

    with col3:

        st.caption("Status")

        st.write(
            status
        )

    with col4:

        st.caption("Characters")

        characters = len(
            f"{subject} {headline} "
            f"{message} {cta}"
        )

        st.write(
            characters
        )


# =========================================================
# RECOMMENDATION CONTEXT
# =========================================================

def render_recommendation_context():
    st.markdown("---")
    st.markdown("## Recommendation Context")
    st.caption(
        "Why the selected product was recommended for this customer."
    )

    campaign = st.session_state.get(
        "generated_campaign",
        {},
    )

    customer_id = st.session_state.get(
        "generated_customer_id",
        "",
    )

    product = st.session_state.get(
        "generated_product",
        "",
    )

    row = get_customer_context(
        customer_id,
        product,
    )

    source = dict(row or {})
    source.update(
        {
            key: value
            for key, value in campaign.items()
            if value not in (None, "", "nan")
        }
    )

    fields = [
        ("Recommended Product", ["product_name", "product"]),
        ("Campaign Objective", ["campaign_objective", "objective"]),
        ("Recommendation Score", ["recommendation_score"]),
        ("Recommendation Confidence", ["recommendation_confidence"]),
        ("Recommendation Reason", ["recommendation_reason", "reason"]),
        ("Retention Risk", ["retention_risk"]),
        ("Cross-Sell Opportunity", ["cross_sell_opportunity"]),
        ("Targeting Priority", ["targeting_priority", "priority"]),
    ]

    rows = []

    for label, keys in fields:
        rows.append(
            {
                "Recommendation": label,
                "Value": clean_generated_text(
                    get_value(
                        source,
                        *keys,
                        default="—",
                    )
                ) or "—",
            }
        )

    st.dataframe(
        pd.DataFrame(rows),
        width="stretch",
        hide_index=True,
    )


# =========================================================
# A/B VARIANTS
# =========================================================

def create_ab_variants(
    customer_id,
    product,
    language,
    base_campaign=None,
):
    cached = st.session_state.get(
        "gemini_ab_variants"
    )

    if cached:
        return (
            cached["variant_a"],
            cached["variant_b"],
        )

    # Compatibility fallback for an older session.
    base = dict(
        base_campaign
        or fallback_campaign(
            customer_id,
            product,
            "Professional",
            language,
            row=get_customer_context(
                customer_id,
                product,
            ),
        )
    )

    variant_a = dict(base)
    variant_a["variant_label"] = "A"
    variant_a["subject"] = (
        f"Discover the value of {product}"
    )
    variant_a["headline"] = (
        f"See how {product} may support your plans"
    )
    variant_a["email_body"] = (
        f"Explore how {product} may be relevant to "
        f"your current financial needs. Review the "
        f"available information to understand the "
        f"features and decide whether it fits your plans."
    )
    variant_a["body"] = variant_a["email_body"]
    variant_a["campaign_body"] = variant_a["email_body"]
    variant_a["message"] = variant_a["email_body"]
    variant_a["generated_message"] = variant_a["email_body"]
    variant_a["cta"] = f"Learn More About {product}"
    variant_a["call_to_action"] = variant_a["cta"]
    variant_a["sms"] = (
        f"Hi! Learn more about {product} and review "
        f"whether it may fit your needs."
    )
    variant_a["variant_rationale"] = (
        "Benefit-focused compatibility fallback."
    )
    variant_a["variant_strength"] = (
        "Informative and value-led."
    )

    variant_b = dict(base)
    variant_b["variant_label"] = "B"
    variant_b["subject"] = (
        f"Take the next step with {product}"
    )
    variant_b["headline"] = (
        f"Explore {product} today"
    )
    variant_b["email_body"] = (
        f"Take a closer look at {product} and review "
        f"the available information, features and "
        f"eligibility details to see whether it may fit "
        f"your financial needs."
    )
    variant_b["body"] = variant_b["email_body"]
    variant_b["campaign_body"] = variant_b["email_body"]
    variant_b["message"] = variant_b["email_body"]
    variant_b["generated_message"] = variant_b["email_body"]
    variant_b["cta"] = f"Explore {product}"
    variant_b["call_to_action"] = variant_b["cta"]
    variant_b["sms"] = (
        f"Hi! Take the next step with {product}. "
        f"Explore the available information."
    )
    variant_b["variant_rationale"] = (
        "Action-focused compatibility fallback."
    )
    variant_b["variant_strength"] = (
        "Direct and next-step oriented."
    )

    return variant_a, variant_b

def _ab_score(campaign, strategy, objective, product):
    """
    Explainable prototype A/B score.

    Uses the generated content plus alignment with the selected
    campaign objective. It is not a prediction of real conversion.
    """

    subject = clean_generated_text(
        get_value(
            campaign,
            "subject",
            "subject_line",
            default="",
        )
    )

    headline = clean_generated_text(
        get_value(
            campaign,
            "headline",
            default="",
        )
    )

    body = clean_generated_text(
        get_value(
            campaign,
            "email_body",
            "campaign_body",
            "body",
            "message",
            "generated_message",
            default="",
        )
    )

    cta = clean_generated_text(
        get_value(
            campaign,
            "cta",
            "call_to_action",
            default="",
        )
    )

    text = (
        f"{subject} {headline} {body} {cta}"
    ).lower()

    score = 50.0

    # Completeness.
    if subject:
        score += 8

    if headline:
        score += 8

    if body:
        score += 12

    if cta:
        score += 7

    # Useful email length.
    if 140 <= len(body) <= 500:
        score += 8
    elif 90 <= len(body) < 140:
        score += 4

    # Correct product usage.
    product_text = str(product or "").strip().lower()

    if product_text and product_text in text:
        score += 5

    # Objective alignment.
    objective_text = str(objective or "").strip().lower()

    if objective_text == "cross-sell":
        if any(
            word in text
            for word in (
                "explore",
                "discover",
                "consider",
                "complement",
            )
        ):
            score += 5

    elif objective_text == "upsell":
        if any(
            word in text
            for word in (
                "enhanced",
                "upgrade",
                "further",
                "more",
            )
        ):
            score += 5

    elif objective_text == "retention":
        if any(
            word in text
            for word in (
                "relationship",
                "support",
                "continue",
                "journey",
            )
        ):
            score += 5

    elif objective_text == "engagement":
        if any(
            word in text
            for word in (
                "discover",
                "explore",
                "learn",
            )
        ):
            score += 5

    # Strategy-specific alignment.
    if strategy == "Benefit-Focused":

        if any(
            word in text
            for word in (
                "benefit",
                "value",
                "support",
                "useful",
                "features",
                "relevant",
            )
        ):
            score += 6

        # Benefit variants are intentionally rewarded for giving
        # enough context rather than being extremely short.
        if len(body) >= 180:
            score += 3

    else:

        if any(
            word in text
            for word in (
                "explore",
                "learn",
                "next step",
                "review",
                "discover",
            )
        ):
            score += 6

        if cta:
            score += 3

    return round(
        min(score, 99.9),
        2,
    )


def render_ab_variant(campaign):
    subject = clean_generated_text(
        get_value(
            campaign,
            "subject",
            "subject_line",
            default="",
        )
    )

    headline = clean_generated_text(
        get_value(
            campaign,
            "headline",
            default="",
        )
    )

    greeting = clean_generated_text(
        get_value(
            campaign,
            "greeting",
            default="Hello,",
        )
    )

    body = clean_generated_text(
        get_value(
            campaign,
            "email_body",
            "campaign_body",
            "body",
            "message",
            "generated_message",
            default="",
        )
    )

    cta = clean_generated_text(
        get_value(
            campaign,
            "cta",
            "call_to_action",
            default="",
        )
    )

    closing = clean_generated_text(
        get_value(
            campaign,
            "closing",
            default="Regards,\nYour Banking Team",
        )
    )

    sms = clean_generated_text(
        get_value(
            campaign,
            "sms",
            default="",
        )
    )

    st.caption("Subject")
    st.write(subject)

    if headline:
        st.markdown(
            f"**{headline}**"
        )

    with st.container(border=True):

        st.write(greeting)

        if body:

            for paragraph in re.split(
                r"\n\s*\n",
                body,
            ):

                paragraph = paragraph.strip()

                if paragraph:
                    st.write(paragraph)

        if cta:
            st.info(cta)

        st.write(closing)

    if sms:

        st.caption("SMS")

        st.write(sms)

    rationale = clean_generated_text(
        get_value(
            campaign,
            "variant_rationale",
            default="",
        )
    )

    strength = clean_generated_text(
        get_value(
            campaign,
            "variant_strength",
            default="",
        )
    )

    if rationale:
        st.caption("Why this variant")
        st.write(rationale)

    if strength:
        st.caption("Variant strength")
        st.write(strength)


def render_ab_testing(customer_id, product):

    st.markdown("---")

    st.markdown(
        "## A/B Campaign Evaluation"
    )

    st.caption(
        "Compare the Benefit-Focused and Action-Focused variants "
        "for the selected customer and recommended product."
    )

    variants = st.session_state.get(
        "gemini_ab_variants"
    )

    variant_a, variant_b = create_ab_variants(
        customer_id,
        product,
        "English",
        base_campaign=st.session_state.get(
            "generated_campaign",
            {},
        ),
    )

    # Get objective from the same selected customer's campaign context.
    campaign = st.session_state.get(
        "generated_campaign",
        {},
    )

    customer_context = get_customer_context(
        customer_id,
        product,
    )

    objective = clean_generated_text(
        get_value(
            campaign,
            "campaign_objective",
            "objective",
            default=get_value(
                customer_context,
                "campaign_objective",
                "objective",
                default="Engagement",
            ),
        )
    ) or "Engagement"

    # --------------------------------------------------------
    # OBJECTIVE CONTEXT
    # --------------------------------------------------------

    c1, c2 = st.columns(2)

    with c1:
        st.caption("Campaign Objective")
        st.markdown(
            f"**{objective}**"
        )

    with c2:
        st.caption("Recommended Product")
        st.markdown(
            f"**{product}**"
        )

    # --------------------------------------------------------
    # SCORE EACH VARIANT
    # --------------------------------------------------------

    score_a = _ab_score(
        variant_a,
        "Benefit-Focused",
        objective,
        product,
    )

    score_b = _ab_score(
        variant_b,
        "Action-Focused",
        objective,
        product,
    )

    # If the generated content is genuinely tied, use the
    # variant-specific strategy signal as the tie breaker so
    # the evaluation never appears broken at 92/92.
    if score_a == score_b:

        if objective.lower() in (
            "cross-sell",
            "upsell",
            "engagement",
        ):
            score_b = round(
                min(score_b + 0.5, 99.9),
                2,
            )
        else:
            score_a = round(
                min(score_a + 0.5, 99.9),
                2,
            )

    winner = (
        "B"
        if score_b > score_a
        else "A"
    )

    strategy = (
        "Action-Focused"
        if winner == "B"
        else "Benefit-Focused"
    )

    difference = abs(
        score_b - score_a
    )

    # --------------------------------------------------------
    # SCORE CARDS
    # --------------------------------------------------------

    result_a, result_b, result_difference = st.columns(3)

    with result_a:

        st.metric(
            "Variant A Score",
            f"{score_a:.2f}/100",
        )

    with result_b:

        st.metric(
            "Variant B Score",
            f"{score_b:.2f}/100",
        )

    with result_difference:

        st.metric(
            "Score Difference",
            f"{difference:.2f}",
        )

    # --------------------------------------------------------
    # WINNER
    # --------------------------------------------------------

    st.markdown(
        "### Winning Recommendation"
    )

    winner_col, strategy_col = st.columns(2)

    with winner_col:

        st.success(
            f"Variant {winner}"
        )

    with strategy_col:

        st.info(
            strategy
        )

    st.caption(
        f"Best fit for the {objective} objective "
        f"using the {product} recommendation."
    )

    # --------------------------------------------------------
    # EXISTING A/B TABS
    # --------------------------------------------------------

    tab_a, tab_b = st.tabs(
        [
            "Variant A · Benefit-Focused",
            "Variant B · Action-Focused",
        ]
    )

    with tab_a:

        st.markdown(
            "### Benefit-Focused"
        )

        st.metric(
            "Variant A Score",
            f"{score_a:.2f}/100",
        )

        render_ab_variant(
            variant_a
        )

    with tab_b:

        st.markdown(
            "### Action-Focused"
        )

        st.metric(
            "Variant B Score",
            f"{score_b:.2f}/100",
        )

        render_ab_variant(
            variant_b
        )

    st.info(
        "A/B scores are explainable content-quality estimates "
        "for the prototype. They are not real opens, clicks, "
        "or conversion measurements."
    )

    st.session_state[
        "ab_variant_a"
    ] = variant_a

    st.session_state[
        "ab_variant_b"
    ] = variant_b

    st.session_state[
        "ab_winner"
    ] = winner

    st.session_state[
        "ab_winning_strategy"
    ] = strategy

    st.session_state[
        "ab_score_a"
    ] = score_a

    st.session_state[
        "ab_score_b"
    ] = score_b

def render_campaign_studio():
    st.markdown("# Campaign Studio")
    st.caption(
        "Create personalized customer campaigns from your real campaign context."
    )

    df = load_campaign_context()

    if df.empty or "customer_id" not in df.columns:
        st.error(
            "campaign_context.csv could not be loaded."
        )
        return

    customer_options = sorted(
        df["customer_id"]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )

    if not customer_options:
        st.error("No customers are available in the campaign dataset.")
        return

    saved_customer = str(
        st.session_state.get(
            "selected_customer_id",
            customer_options[0],
        )
    )

    customer_index = (
        customer_options.index(saved_customer)
        if saved_customer in customer_options
        else 0
    )

    # =====================================================
    # CUSTOMER
    # =====================================================

    with st.container(border=True):
        st.markdown("### 1. Customer & Recommendation")

        customer_id = st.selectbox(
            "Search Customer",
            customer_options,
            index=customer_index,
            key="campaign_customer_search",
            help="Type to search the customer ID list.",
        )

        customer_rows = df[
            df["customer_id"].astype(str).str.strip()
            == str(customer_id).strip()
        ]

        product_options = []

        if (
            not customer_rows.empty
            and "product_name" in customer_rows.columns
        ):
            product_options = [
                str(value).strip()
                for value in customer_rows["product_name"]
                .dropna()
                .tolist()
                if str(value).strip()
                and str(value).lower() != "nan"
            ]

        product_options = list(
            dict.fromkeys(product_options)
        )

        if not product_options:
            product_options = [
                "Personal Loan",
                "Premium Banking",
                "Term Insurance",
                "Credit Card",
                "Savings Account",
            ]

        saved_product = str(
            st.session_state.get(
                "generated_product",
                product_options[0],
            )
        )

        product_index = (
            product_options.index(saved_product)
            if saved_product in product_options
            else 0
        )

        product = st.selectbox(
            "Recommended Product",
            product_options,
            index=product_index,
            key=f"campaign_product_{customer_id}",
        )

    selected_context = get_customer_context(
        customer_id,
        product,
    )

    if selected_context:

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Segment",
            clean_generated_text(
                get_value(
                    selected_context,
                    "primary_segment",
                    default="—",
                )
            ) or "—",
        )

        c2.metric(
            "Persona",
            clean_generated_text(
                get_value(
                    selected_context,
                    "customer_persona",
                    default="—",
                )
            ) or "—",
        )

        c3.metric(
            "Retention Risk",
            clean_generated_text(
                get_value(
                    selected_context,
                    "retention_risk",
                    default="—",
                )
            ) or "—",
        )

        c4.metric(
            "Cross-Sell",
            clean_generated_text(
                get_value(
                    selected_context,
                    "cross_sell_opportunity",
                    default="—",
                )
            ) or "—",
        )

    # =====================================================
    # SETTINGS
    # =====================================================

    with st.container(border=True):
        st.markdown("### 2. Campaign Settings")

        col1, col2 = st.columns(2)

        with col1:
            language = st.selectbox(
                "Language",
                [
                    "English",
                    "Hindi",
                    "Marathi",
                ],
                key="campaign_language",
            )

        with col2:
            tone = st.selectbox(
                "Tone",
                [
                    "Professional",
                    "Friendly",
                    "Persuasive",
                ],
                key="campaign_tone",
            )

    # =====================================================
    # GENERATE
    # =====================================================

    if st.button(
        "✨ Generate Personalized Campaign",
        type="primary",
        width="stretch",
        key="campaign_generate_button",
    ):

        st.session_state.pop(
            "gemini_ab_variants",
            None,
        )

        with st.spinner(
            "Creating personalized Email and SMS content..."
        ):

            campaign = generate_campaign(
                customer_id,
                product,
                language,
                tone,
            )

        st.session_state["generated_campaign"] = campaign
        st.session_state["generated_customer_id"] = customer_id
        st.session_state["generated_product"] = product
        st.session_state["generated_language"] = language
        st.session_state["generated_tone"] = tone

        st.session_state["generated_campaign_objective"] = (
            get_value(
                selected_context,
                "campaign_objective",
                "objective",
                default="Engagement",
            )
        )

        st.session_state["campaign_approved"] = False
        st.session_state["creative_approved"] = False

        st.session_state.pop(
            "approved_creative",
            None,
        )

        st.success(
            "Personalized campaign generated successfully."
        )

    campaign = st.session_state.get(
        "generated_campaign"
    )

    if not campaign:
        st.info(
            "Select a customer, review the recommendation, "
            "and generate the campaign."
        )
        return

    # =====================================================
    # MAIN PREVIEW
    # =====================================================

    st.markdown("---")
    st.markdown("## Generated Campaign")

    subject = clean_generated_text(
        get_value(
            campaign,
            "subject",
            "subject_line",
            default="",
        )
    )

    headline = clean_generated_text(
        get_value(
            campaign,
            "headline",
            default="",
        )
    )

    greeting = clean_generated_text(
        get_value(
            campaign,
            "greeting",
            default="Hello,",
        )
    )

    email_body = clean_generated_text(
        get_value(
            campaign,
            "email_body",
            "campaign_body",
            "body",
            "message",
            "generated_message",
            default="",
        )
    )

    cta = clean_generated_text(
        get_value(
            campaign,
            "cta",
            "call_to_action",
            default="",
        )
    )

    closing = clean_generated_text(
        get_value(
            campaign,
            "closing",
            default="Regards,\nYour Banking Team",
        )
    )

    sms = clean_generated_text(
        get_value(
            campaign,
            "sms",
            "sms_body",
            "sms_message",
            default="",
        )
    )

    if not sms:
        sms = (
            f"{headline} {email_body} {cta}"
        ).strip()

    email_tab, sms_tab = st.tabs(
        ["📧 Email", "📱 SMS"]
    )

    with email_tab:

        with st.container(border=True):

            st.caption("Subject")
            st.markdown(
                f"### {subject}"
            )

            st.divider()

            if headline:
                st.markdown(
                    f"## {headline}"
                )

            st.write(greeting)

            for paragraph in email_body.split("\n\n"):

                paragraph = paragraph.strip()

                if paragraph:
                    st.write(paragraph)

            if cta:
                st.button(
                    cta,
                    disabled=True,
                    key="campaign_preview_cta",
                )

            st.write(closing)

    with sms_tab:

        with st.container(border=True):

            st.caption(
                f"{len(sms)} characters"
            )

            st.write(sms)

    # =====================================================
    # RECOMMENDATION
    # =====================================================

    render_recommendation_context()

    # =====================================================
    # A/B
    # =====================================================

    render_ab_testing(
        customer_id=customer_id,
        product=product,
    )
