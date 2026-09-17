import json
import re
from pathlib import Path

import pandas as pd

from src.campaign.gemini_client import generate_text


# ============================================================
# GEMINI CONTROL
# ============================================================

GEMINI_DISABLED = False


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]
PROCESSED_DIR = BASE_DIR / "data" / "processed"

CONTEXT_FILE = PROCESSED_DIR / "campaign_context.csv"
OUTPUT_FILE = PROCESSED_DIR / "campaign_content.csv"

SUPPORTED_LANGUAGES = ["English", "Hindi", "Marathi"]
SUPPORTED_STRATEGIES = ["Benefit-Focused", "Action-Focused"]


# ============================================================
# LANGUAGE / STRATEGY
# ============================================================

def language_instruction(language):
    language = (
        language
        if language in SUPPORTED_LANGUAGES
        else "English"
    )

    return {
        "English": (
            "Write customer-facing Email and SMS content in natural, "
            "professional English."
        ),
        "Hindi": (
            "Write customer-facing Email and SMS content in natural, "
            "professional Hindi using Devanagari script."
        ),
        "Marathi": (
            "Write customer-facing Email and SMS content in natural, "
            "professional Marathi using Devanagari script."
        ),
    }[language]


def strategy_instruction(strategy):
    if strategy == "Benefit-Focused":
        return (
            "Benefit-Focused: emphasize relevant customer value, usefulness, "
            "convenience and product relevance before the call to action."
        )

    if strategy == "Action-Focused":
        return (
            "Action-Focused: emphasize a concise, clear and low-pressure "
            "next step for the customer."
        )

    return (
        "Balanced: provide a relevant and professional introduction "
        "to the recommended product."
    )


def internal_rationale(strategy):
    """
    Internal A/B rationale is intentionally English.
    It is not customer-facing and must not change with language.
    """
    if strategy == "Benefit-Focused":
        return (
            "Technical rationale: prioritizes value framing and relevance "
            "before the call to action. This tests whether benefit-led "
            "messaging improves engagement for the selected audience."
        )

    if strategy == "Action-Focused":
        return (
            "Technical rationale: prioritizes a concise next step and direct "
            "response framing. This tests whether action-led messaging "
            "improves engagement relative to benefit-led framing."
        )

    return (
        "Technical rationale: balances relevance, customer value and "
        "next-step clarity."
    )


def internal_strength(strategy):
    if strategy == "Benefit-Focused":
        return "Value communication and relevance"

    if strategy == "Action-Focused":
        return "Clear next-step communication"

    return "Balanced relevance"


# ============================================================
# GEMINI PROMPT
# ============================================================

def build_campaign_prompt(
    row,
    language="English",
    tone="Professional",
    strategy=None,
):
    language = (
        language
        if language in SUPPORTED_LANGUAGES
        else "English"
    )

    strategy = strategy or "Balanced"

    return f"""
You are an AI marketing campaign generator for a banking institution.

Create a personalized campaign using ONLY the customer and recommendation
information supplied below.

CUSTOMER INFORMATION
--------------------
Customer ID: {row.get('customer_id', '')}
Customer Name: {row.get('customer_name', row.get('name', ''))}
Primary Segment: {row.get('primary_segment', '')}
Customer Persona: {row.get('customer_persona', '')}
Retention Risk: {row.get('retention_risk', '')}
Cross-Sell Opportunity: {row.get('cross_sell_opportunity', '')}
GenAI Targeting Priority: {row.get('genai_targeting_priority', '')}

CAMPAIGN INFORMATION
--------------------
Campaign Objective: {row.get('campaign_objective', '')}
Recommended Product: {row.get('product_name', '')}
Marketing Angle: {row.get('marketing_angle', '')}
Campaign Priority: {row.get('campaign_priority', '')}
Recommendation Score: {row.get('recommendation_score', '')}
Recommendation Confidence: {row.get('recommendation_confidence', '')}
Recommendation Reason: {row.get('recommendation_reason', '')}

GENERATION SETTINGS
-------------------
Selected Content Language: {language}
Selected Tone: {tone}
A/B Strategy: {strategy}

LANGUAGE RULE
-------------
{language_instruction(language)}

IMPORTANT:
- Only customer-facing Email and SMS content should use the selected language.
- The A/B strategy name must remain exactly "{strategy}".
- The technical variant rationale MUST remain in professional English.
- The technical variant strength MUST remain in professional English.
- Do not translate or rename "Benefit-Focused" or "Action-Focused".
- Changing language must NOT change the strategy definition.

STRATEGY RULE
-------------
{strategy_instruction(strategy)}

CONTENT RULES
-------------
- Match the campaign objective.
- Promote the recommended product.
- Reflect the available customer segment/persona and recommendation context.
- Do not invent names, balances, rates, approvals, dates, eligibility or offers.
- Do not guarantee approval, savings, returns or benefits.
- Do not mention internal scores, segmentation systems, AI or model reasoning
  to the customer.
- Keep Email content substantially more detailed than SMS content.
- SMS must be concise and suitable for a mobile channel.
- Do not return HTML tags.
- Do not return CSS.
- Do not return Markdown code fences.
- Do not return an HTML email template.
- Customer-facing fields must contain plain text only.
- Technical rationale and technical strength are internal fields.

Return ONLY valid JSON in exactly this structure:

{{
    "subject": "...",
    "headline": "...",
    "greeting": "...",
    "email_body": "...",
    "cta": "...",
    "closing": "...",
    "sms": "...",
    "variant_rationale": "{internal_rationale(strategy)}",
    "variant_strength": "{internal_strength(strategy)}"
}}
"""


# ============================================================
# JSON EXTRACTION
# ============================================================

def extract_json(text):
    text = str(text or "").strip()

    text = re.sub(
        r"^```json\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r"^```\s*",
        "",
        text,
    )
    text = re.sub(
        r"\s*```$",
        "",
        text,
    )

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(
            r"\{.*\}",
            text,
            flags=re.DOTALL,
        )

        if match:
            return json.loads(match.group())

        raise ValueError(
            "Gemini response did not contain valid JSON."
        )


# ============================================================
# FALLBACK
# ============================================================

def fallback_campaign(
    row,
    language="English",
    tone="Professional",
    strategy=None,
):
    product = str(
        row.get(
            "product_name",
            "our banking product",
        )
    )

    objective = str(
        row.get(
            "campaign_objective",
            "Engagement",
        )
    )

    strategy = strategy or "Balanced"

    rationale = internal_rationale(strategy)
    strength = internal_strength(strategy)

    if language == "Hindi":
        if strategy == "Benefit-Focused":
            return {
                "subject": f"{product} के लाभों को जानें",
                "headline": f"आपकी वित्तीय जरूरतों के लिए {product}",
                "greeting": "नमस्ते!",
                "email_body": (
                    f"आपके बैंकिंग संबंध और उपलब्ध संदर्भ को ध्यान में रखते हुए, "
                    f"{product} आपकी वित्तीय जरूरतों के लिए एक उपयोगी विकल्प हो सकता है। "
                    f"उपलब्ध जानकारी देखें और तय करें कि यह आपके लिए उपयुक्त है या नहीं।"
                ),
                "cta": f"{product} के बारे में जानें",
                "closing": "सादर,\nआपकी बैंकिंग टीम",
                "sms": (
                    f"नमस्ते! {product} आपकी वित्तीय जरूरतों के लिए एक उपयोगी "
                    f"विकल्प हो सकता है। अधिक जानकारी देखें।"
                ),
                "variant_rationale": rationale,
                "variant_strength": strength,
            }

        return {
            "subject": f"{product} के साथ अगला कदम जानें",
            "headline": f"{product} के विकल्प देखें",
            "greeting": "नमस्ते!",
            "email_body": (
                f"{product} के बारे में अधिक जानकारी देखें और जानें कि यह "
                f"आपकी वित्तीय जरूरतों के लिए उपयुक्त हो सकता है या नहीं।"
            ),
            "cta": f"{product} देखें",
            "closing": "सादर,\nआपकी बैंकिंग टीम",
            "sms": (
                f"नमस्ते! {product} के बारे में अधिक जानें और देखें कि यह "
                f"आपकी जरूरतों के लिए उपयुक्त हो सकता है या नहीं।"
            ),
            "variant_rationale": rationale,
            "variant_strength": strength,
        }

    if language == "Marathi":
        if strategy == "Benefit-Focused":
            return {
                "subject": f"{product} चे फायदे जाणून घ्या",
                "headline": f"तुमच्या आर्थिक गरजांसाठी {product}",
                "greeting": "नमस्कार!",
                "email_body": (
                    f"तुमच्या बँकिंग संबंधांचा विचार करता, {product} हा तुमच्या "
                    f"आर्थिक गरजांसाठी उपयुक्त पर्याय ठरू शकतो. उपलब्ध माहिती "
                    f"पाहून तो तुमच्यासाठी योग्य आहे का ते जाणून घ्या."
                ),
                "cta": f"{product} बद्दल जाणून घ्या",
                "closing": "आपला,\nतुमची बँकिंग टीम",
                "sms": (
                    f"नमस्कार! {product} तुमच्या आर्थिक गरजांसाठी उपयुक्त पर्याय "
                    f"ठरू शकतो. अधिक माहिती पाहा."
                ),
                "variant_rationale": rationale,
                "variant_strength": strength,
            }

        return {
            "subject": f"{product} सोबत पुढचे पाऊल जाणून घ्या",
            "headline": f"{product} चे पर्याय पाहा",
            "greeting": "नमस्कार!",
            "email_body": (
                f"{product} बद्दल अधिक माहिती पाहा आणि तो तुमच्या आर्थिक "
                f"गरजांसाठी योग्य आहे का ते जाणून घ्या."
            ),
            "cta": f"{product} पाहा",
            "closing": "आपला,\nतुमची बँकिंग टीम",
            "sms": (
                f"नमस्कार! {product} बद्दल अधिक जाणून घ्या आणि तो तुमच्या "
                f"गरजांसाठी योग्य आहे का ते पाहा."
            ),
            "variant_rationale": rationale,
            "variant_strength": strength,
        }

    if strategy == "Benefit-Focused":
        subject = f"Discover more value with {product}"
        headline = f"See how {product} may support your needs"
        email_body = (
            f"Based on the available customer context, {product} could be "
            f"a useful option for your financial needs. Review the available "
            f"information to see whether it fits your plans."
        )
        cta = f"Learn More About {product}"
        sms = (
            f"Hi! Explore {product} and see whether it may fit your "
            f"financial needs. Learn more."
        )

    elif strategy == "Action-Focused":
        subject = f"Take the next step with {product}"
        headline = f"Explore {product}"
        email_body = (
            f"Take a closer look at {product} and review the available "
            f"information to see whether it may fit your financial needs."
        )
        cta = f"Explore {product}"
        sms = (
            f"Hi! Take a closer look at {product} and see whether it may "
            f"fit your financial needs. Learn more."
        )

    elif objective == "Retention":
        subject = "We are here to support your financial journey"
        headline = "Keep getting more from your banking relationship"
        email_body = (
            f"We value your relationship with us. Explore how {product} "
            f"may support your evolving financial needs."
        )
        cta = f"Learn More About {product}"
        sms = (
            f"Hi! Explore how {product} may support your financial needs. "
            f"Learn more."
        )

    else:
        subject = f"Discover more with {product}"
        headline = "An option worth exploring"
        email_body = (
            f"Explore {product} and review the available information to see "
            f"whether it may complement your financial needs."
        )
        cta = f"Explore {product}"
        sms = (
            f"Hi! Explore {product} and see whether it may fit your "
            f"financial needs. Learn more."
        )

    return {
        "subject": subject,
        "headline": headline,
        "greeting": "Hello,",
        "email_body": email_body,
        "cta": cta,
        "closing": "Regards,\nYour Banking Team",
        "sms": sms,
        "variant_rationale": rationale,
        "variant_strength": strength,
    }


# ============================================================
# NORMALIZATION
# ============================================================

def strip_html(value):
    text = str(value or "")
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("```html", "")
    text = text.replace("```", "")
    return text.strip()


def normalize_campaign(
    campaign,
    row,
    language="English",
    tone="Professional",
    strategy=None,
):
    strategy = strategy or "Balanced"

    fallback = fallback_campaign(
        row,
        language,
        tone,
        strategy,
    )

    campaign = dict(campaign or {})

    aliases = {
        "subject": [
            "subject",
            "subject_line",
        ],
        "headline": [
            "headline",
            "title",
        ],
        "email_body": [
            "email_body",
            "body",
            "campaign_body",
            "message",
            "generated_message",
            "content",
        ],
        "cta": [
            "cta",
            "call_to_action",
            "call_to_action_text",
        ],
    }

    normalized = {}

    for target, keys in aliases.items():
        value = ""

        for key in keys:
            candidate = campaign.get(key)

            if candidate is not None and str(candidate).strip():
                value = candidate
                break

        normalized[target] = (
            strip_html(value)
            if value
            else fallback[target]
        )

    for key in [
        "greeting",
        "closing",
        "sms",
    ]:
        value = campaign.get(key)

        normalized[key] = (
            strip_html(value)
            if value
            else fallback[key]
        )

    # A/B technical metadata is always English/internal.
    normalized["variant_rationale"] = internal_rationale(
        strategy
    )

    normalized["variant_strength"] = internal_strength(
        strategy
    )

    normalized.update(
        {
            "campaign_id": campaign.get(
                "campaign_id",
                f"GEN-{row.get('customer_id', '000001')}",
            ),
            "product_name": row.get(
                "product_name",
                "",
            ),
            "campaign_objective": row.get(
                "campaign_objective",
                "",
            ),
            "generation_mode": campaign.get(
                "generation_mode",
                "GenAI Campaign Pipeline",
            ),
            "compliance": campaign.get(
                "compliance",
                "PENDING REVIEW",
            ),
            "status": campaign.get(
                "status",
                "Generated",
            ),
            "language": language,
            "tone": tone,
            "strategy": strategy,
        }
    )

    return normalized


# ============================================================
# GENERATE ONE CAMPAIGN
# ============================================================

def generate_campaign(
    row,
    language="English",
    tone="Professional",
    strategy=None,
):
    global GEMINI_DISABLED

    if language not in SUPPORTED_LANGUAGES:
        language = "English"

    if strategy not in SUPPORTED_STRATEGIES:
        strategy = strategy or "Balanced"

    if GEMINI_DISABLED:
        return (
            normalize_campaign(
                fallback_campaign(
                    row,
                    language,
                    tone,
                    strategy,
                ),
                row,
                language,
                tone,
                strategy,
            ),
            "Fallback",
        )

    prompt = build_campaign_prompt(
        row,
        language=language,
        tone=tone,
        strategy=strategy,
    )

    try:
        response = generate_text(prompt)
        campaign = extract_json(response)

        required_fields = [
            "subject",
            "headline",
            "greeting",
            "email_body",
            "cta",
            "closing",
            "sms",
            "variant_rationale",
            "variant_strength",
        ]

        for field in required_fields:
            if (
                field not in campaign
                or not str(campaign[field]).strip()
            ):
                raise ValueError(
                    f"Missing or empty field: {field}"
                )

        return (
            normalize_campaign(
                campaign,
                row,
                language,
                tone,
                strategy,
            ),
            "Gemini",
        )

    except Exception as error:
        error_text = str(error)

        print(
            f"WARNING - Gemini generation failed for "
            f"{row.get('customer_id')}: {error}"
        )

        if (
            "quota" in error_text.lower()
            or "429" in error_text
            or "RESOURCE_EXHAUSTED" in error_text
        ):
            GEMINI_DISABLED = True

        return (
            normalize_campaign(
                fallback_campaign(
                    row,
                    language,
                    tone,
                    strategy,
                ),
                row,
                language,
                tone,
                strategy,
            ),
            "Fallback",
        )


# ============================================================
# BATCH GENERATION - PRESERVED FROM ORIGINAL PIPELINE
# ============================================================

def main():
    print("=" * 70)
    print("PHASE 5C - AI CAMPAIGN CONTENT GENERATION")
    print("=" * 70)

    if not CONTEXT_FILE.exists():
        raise FileNotFoundError(
            f"Campaign context not found:\n{CONTEXT_FILE}"
        )

    df = pd.read_csv(CONTEXT_FILE)

    print(
        f"Campaign contexts loaded : {len(df):,}"
    )

    print(
        f"Unique customers         : "
        f"{df['customer_id'].nunique():,}"
    )

    results = []

    for index, row in df.iterrows():
        if (index + 1) % 25 == 0:
            print(
                f"Generated campaigns: "
                f"{index + 1:,}/{len(df):,}"
            )

        campaign, source = generate_campaign(
            row.to_dict()
        )

        result = row.to_dict()

        result.update(
            {
                "subject": campaign["subject"],
                "headline": campaign["headline"],
                "campaign_body": campaign["email_body"],
                "cta": campaign["cta"],
                "sms": campaign["sms"],
                "greeting": campaign["greeting"],
                "closing": campaign["closing"],
                "generation_source": source,
                "variant_rationale": campaign[
                    "variant_rationale"
                ],
                "variant_strength": campaign[
                    "variant_strength"
                ],
            }
        )

        results.append(result)

    output = pd.DataFrame(results)
    output.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print("\nCampaign content saved to:")
    print(OUTPUT_FILE)

    print(
        f"Rows    : {len(output):,}"
    )

    print(
        f"Columns : {len(output.columns):,}"
    )


if __name__ == "__main__":
    main()
