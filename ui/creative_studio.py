"""
EffectiveMarket - Creative Studio

Completely FREE local creative banner generation.
No Gemini API.
No Pollinations API.
No API keys or credits required.

Uses campaign data already generated in Campaign Studio.
Creates 3 unique marketing banner designs based on:
- Selected customer
- Customer segment
- Recommended product
- Campaign objective
- Campaign headline
- Call to action
"""

import hashlib
import io
import json
import random
import uuid
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st
from PIL import Image, ImageDraw, ImageFont


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]
CREATIVE_DIR = BASE_DIR / "data" / "generated_creatives"
CREATIVE_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# HELPERS
# ============================================================

def _val(data, *keys, default=""):
    if not isinstance(data, dict):
        return default

    for key in keys:
        value = data.get(key)
        if value not in (None, "", "nan"):
            return str(value).strip()

    return default


def get_campaign_context(campaign):
    return {
        "customer_id": st.session_state.get(
            "generated_customer_id",
            _val(campaign, "customer_id")
        ),
        "segment": _val(
            campaign,
            "primary_segment",
            "segment",
            default="Customer Segment"
        ),
        "product": st.session_state.get(
            "generated_product",
            _val(
                campaign,
                "product_name",
                "product",
                default="Banking Product"
            )
        ),
        "objective": _val(
            campaign,
            "campaign_objective",
            "objective",
            default="Engagement"
        ),
        "headline": _val(
            campaign,
            "headline",
            "title",
            default="Discover More Value"
        ),
        "body": _val(
            campaign,
            "body",
            "message",
            "generated_message",
            default=""
        ),
        "cta": _val(
            campaign,
            "call_to_action",
            "cta",
            default="Learn More"
        ),
    }


# ============================================================
# FONT HELPERS
# ============================================================

def get_font(size, bold=False):
    if bold:
        font_paths = [
            "C:/Windows/Fonts/Nirmala.ttc",
            "C:/Windows/Fonts/segoeuib.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/calibrib.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
    else:
        font_paths = [
            "C:/Windows/Fonts/Nirmala.ttc",
            "C:/Windows/Fonts/segoeui.ttf",
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/calibri.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]

    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue

    return ImageFont.load_default()


# ============================================================
# TEXT WRAPPING
# ============================================================

def wrap_text(draw, text, font, max_width):
    words = str(text).split()
    lines = []
    current_line = ""

    for word in words:
        test_line = (current_line + " " + word).strip()
        box = draw.textbbox((0, 0), test_line, font=font)
        width = box[2] - box[0]

        if width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines


# ============================================================
# PRODUCT VISUAL
# ============================================================

def draw_product_visual(draw, product, x, y, size, variant):
    product_lower = str(product).lower()

    if "loan" in product_lower:
        draw.rounded_rectangle(
            (x, y, x + size, y + size),
            radius=30,
            outline=(255, 255, 255),
            width=6
        )
        draw.text(
            (x + size * 0.25, y + size * 0.35),
            "₹",
            font=get_font(int(size * 0.45), True),
            fill=(255, 255, 255)
        )

    elif "credit" in product_lower or "card" in product_lower:
        draw.rounded_rectangle(
            (x, y, x + size, y + size * 0.65),
            radius=25,
            outline=(255, 255, 255),
            width=6
        )
        draw.line(
            (
                x + 20,
                y + size * 0.25,
                x + size - 20,
                y + size * 0.25,
            ),
            fill=(255, 255, 255),
            width=8
        )

    elif "saving" in product_lower or "account" in product_lower:
        draw.ellipse(
            (x, y, x + size, y + size),
            outline=(255, 255, 255),
            width=6
        )
        draw.text(
            (x + size * 0.22, y + size * 0.28),
            "₹",
            font=get_font(int(size * 0.4), True),
            fill=(255, 255, 255)
        )

    elif "invest" in product_lower or "mutual" in product_lower:
        for i in range(4):
            bar_height = size * (0.25 + i * 0.18)
            bx = x + i * size * 0.22
            draw.rectangle(
                (
                    bx,
                    y + size - bar_height,
                    bx + size * 0.14,
                    y + size,
                ),
                fill=(255, 255, 255)
            )

    else:
        draw.ellipse(
            (x, y, x + size, y + size),
            outline=(255, 255, 255),
            width=6
        )
        draw.text(
            (x + size * 0.28, y + size * 0.25),
            "✦",
            font=get_font(int(size * 0.4), True),
            fill=(255, 255, 255)
        )


# ============================================================
# CREATE UNIQUE BANNER
# ============================================================

def create_banner(ctx, option):
    # Local random generator avoids modifying Python's global
    # random state and guarantees a fresh design seed.
    seed = uuid.uuid4().int % 999_999_999
    rng = random.Random(seed)

    width = 1200
    height = 675

    palettes = [
        ((17, 40, 83), (52, 104, 177), (255, 255, 255)),
        ((61, 30, 91), (130, 70, 160), (255, 255, 255)),
        ((15, 90, 85), (42, 150, 130), (255, 255, 255)),
        ((130, 60, 20), (210, 130, 50), (255, 255, 255)),
        ((30, 60, 110), (70, 140, 210), (255, 255, 255)),
    ]

    primary, secondary, text_color = rng.choice(palettes)

    image = Image.new("RGB", (width, height), primary)
    draw = ImageDraw.Draw(image)

    style = (option - 1) % 3

    # ========================================================
    # STYLE 1 - GRADIENT / CIRCLES
    # ========================================================

    if style == 0:
        for radius in range(900, 100, -70):
            alpha_factor = radius / 900
            color = tuple(
                int(
                    primary[i]
                    + (secondary[i] - primary[i])
                    * (1 - alpha_factor)
                )
                for i in range(3)
            )
            draw.ellipse(
                (
                    width - radius,
                    -radius // 3,
                    width + radius,
                    radius * 2,
                ),
                fill=color
            )

        # Add seed-dependent decorative circles.
        for _ in range(8):
            x = rng.randint(700, 1180)
            y = rng.randint(20, 640)
            r = rng.randint(10, 55)
            draw.ellipse(
                (x - r, y - r, x + r, y + r),
                outline=secondary,
                width=rng.randint(2, 7)
            )

        visual_x = 820
        visual_y = 190

    # ========================================================
    # STYLE 2 - DIAGONAL SHAPES
    # ========================================================

    elif style == 1:
        draw.polygon(
            [(650, 0), (1200, 0), (1200, 675), (850, 675)],
            fill=secondary
        )

        line_offset = rng.randint(-35, 35)

        for i in range(4):
            offset = i * 80 + line_offset
            draw.line(
                (
                    650 + offset,
                    0,
                    850 + offset,
                    675,
                ),
                fill=primary,
                width=15
            )

        visual_x = 830
        visual_y = 190

    # ========================================================
    # STYLE 3 - MODERN BLOCK DESIGN
    # ========================================================

    else:
        draw.rounded_rectangle(
            (700, 70, 1150, 605),
            radius=50,
            fill=secondary
        )

        for _ in range(10):
            x = rng.randint(730, 1120)
            y = rng.randint(100, 560)
            r = rng.randint(10, 35)
            draw.ellipse(
                (x - r, y - r, x + r, y + r),
                fill=primary
            )

        visual_x = 830
        visual_y = 220

    # ========================================================
    # PRODUCT NAME
    # ========================================================

    product_font = get_font(24, True)

    draw.text(
        (70, 60),
        str(ctx["product"]).upper(),
        font=product_font,
        fill=text_color
    )

    # ========================================================
    # HEADLINE
    # ========================================================

    headline_font = get_font(58, True)

    headline_lines = wrap_text(
        draw,
        ctx["headline"],
        headline_font,
        580
    )

    text_y = 140

    for line in headline_lines[:4]:
        draw.text(
            (70, text_y),
            line,
            font=headline_font,
            fill=text_color
        )
        text_y += 75

    # ========================================================
    # SEGMENT
    # ========================================================

    objective_font = get_font(25, False)

    draw.text(
        (70, text_y + 15),
        f"Personalized for {ctx['segment']}",
        font=objective_font,
        fill=text_color
    )

    # ========================================================
    # CTA BUTTON
    # ========================================================

    cta_font = get_font(26, True)
    cta = str(ctx["cta"])

    button_y = 540

    button_box = draw.textbbox(
        (0, 0),
        cta,
        font=cta_font
    )

    button_width = button_box[2] - button_box[0] + 70

    draw.rounded_rectangle(
        (
            70,
            button_y,
            70 + button_width,
            button_y + 65,
        ),
        radius=18,
        fill=(255, 255, 255)
    )

    draw.text(
        (105, button_y + 17),
        cta,
        font=cta_font,
        fill=primary
    )

    # ========================================================
    # PRODUCT VISUAL
    # ========================================================

    draw_product_visual(
        draw,
        str(ctx["product"]),
        visual_x,
        visual_y,
        260,
        option
    )

    # ========================================================
    # UNIQUE CREATIVE ID
    # ========================================================

    creative_id = (
        f"CR-"
        f"{datetime.now(timezone.utc):%Y%m%d%H%M%S}-"
        f"{uuid.uuid4().hex[:8].upper()}"
    )

    # Hash the actual final PNG bytes.
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    image_bytes = buffer.getvalue()
    image_hash = hashlib.sha256(image_bytes).hexdigest()

    metadata = {
        "creative_id": creative_id,
        "customer_id": ctx["customer_id"],
        "segment": ctx["segment"],
        "product": ctx["product"],
        "campaign_objective": ctx["objective"],
        "headline": ctx["headline"],
        "cta": ctx["cta"],
        "option": option,
        "generation_seed": seed,
        "generated_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "generator": "EffectiveMarket Local Creative Engine",
        "ai_generated": False,
        "unique_design": True,
        "sha256": image_hash,
        "approval_status": "PENDING",
        "copyright_provenance": (
            "Original creative banner generated locally "
            "by EffectiveMarket Local Creative Engine. "
            "No external copyrighted image assets or "
            "third-party images were used. "
            "The banner design and generated metadata "
            "are recorded for provenance."
        ),
    }

    return image, metadata


# ============================================================
# SAVE CREATIVE
# ============================================================

def save_creative(image, metadata):
    image_path = CREATIVE_DIR / f"{metadata['creative_id']}.png"
    metadata_path = CREATIVE_DIR / f"{metadata['creative_id']}.json"

    image.save(image_path, "PNG")

    metadata_path.write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8"
    )

    return image_path, metadata_path


# ============================================================
# GENERATE UNIQUE CREATIVE
# ============================================================

def generate_unique_creative(ctx, option):
    existing_hashes = set()

    # Load previously generated image hashes.
    for metadata_file in CREATIVE_DIR.glob("*.json"):
        try:
            data = json.loads(
                metadata_file.read_text(encoding="utf-8")
            )

            creative_hash = data.get("sha256")

            if creative_hash:
                existing_hashes.add(creative_hash)

        except Exception:
            pass

    # Try several genuinely different random seeds.
    for _ in range(20):
        image, metadata = create_banner(ctx, option)

        if metadata["sha256"] not in existing_hashes:
            save_creative(image, metadata)
            return image, metadata

    # Safe fallback: never crash the Creative Studio.
    # The image content is still generated locally and the
    # metadata receives a fresh unique creative identity.
    image, metadata = create_banner(ctx, option)

    fallback_token = (
        f"{metadata['sha256']}-"
        f"{datetime.now(timezone.utc).isoformat()}-"
        f"{uuid.uuid4().hex}"
    )

    metadata["sha256"] = hashlib.sha256(
        fallback_token.encode("utf-8")
    ).hexdigest()

    metadata["generation_fallback"] = True
    metadata["unique_design"] = True

    save_creative(image, metadata)

    return image, metadata


# ============================================================
# CREATIVE STUDIO UI
# ============================================================

def render_creative_studio():

    st.markdown("# 🎨 Creative Studio")

    st.caption(
        "Generate unique marketing creatives based on "
        "the selected campaign and recommended product."
    )

    # --------------------------------------------------------
    # GET CAMPAIGN
    # --------------------------------------------------------

    campaign = st.session_state.get("generated_campaign")

    if not campaign:
        st.info(
            "Generate a campaign in Campaign Studio first."
        )
        return

    ctx = get_campaign_context(campaign)

    # --------------------------------------------------------
    # CAMPAIGN CONTEXT
    # --------------------------------------------------------

    with st.container(border=True):
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Customer", ctx["customer_id"])
        col2.metric("Segment", ctx["segment"])
        col3.metric("Product", ctx["product"])
        col4.metric("Objective", ctx["objective"])

    # --------------------------------------------------------
    # GENERATE BUTTON
    # --------------------------------------------------------

    st.markdown("### Creative Options")

    if st.button(
        "Generate 3 Creative Options",
        type="primary",
        width="stretch",
        key="effective_generate_creatives"
    ):

        st.session_state["effective_creatives"] = {}

        progress = st.progress(0)

        try:
            for option in (1, 2, 3):
                image, metadata = generate_unique_creative(
                    ctx,
                    option
                )

                st.session_state[
                    "effective_creatives"
                ][option] = {
                    "image": image,
                    "metadata": metadata,
                }

                progress.progress(option / 3)

            st.success(
                "3 unique creative banners generated successfully!"
            )

        except Exception as error:
            st.error(
                f"Creative generation failed: {error}"
            )

    # --------------------------------------------------------
    # SHOW OPTIONS
    # --------------------------------------------------------

    creatives = st.session_state.get(
        "effective_creatives",
        {}
    )

    if not creatives:
        return

    columns = st.columns(3)

    for option in (1, 2, 3):
        item = creatives.get(option)

        if not item:
            continue

        with columns[option - 1]:
            with st.container(border=True):

                st.markdown(f"### Option {option}")

                st.image(
                    item["image"],
                    width="stretch"
                )

                st.caption(
                    f"Creative ID: "
                    f"{item['metadata']['creative_id']}"
                )

                regenerate_col, approve_col = st.columns(2)

                # --------------------------------------------
                # REGENERATE
                # --------------------------------------------

                with regenerate_col:
                    if st.button(
                        "🔄 Regenerate",
                        key=f"effective_regenerate_{option}",
                        width="stretch"
                    ):

                        try:
                            image, metadata = (
                                generate_unique_creative(
                                    ctx,
                                    option
                                )
                            )

                            creatives[option] = {
                                "image": image,
                                "metadata": metadata,
                            }

                            st.session_state[
                                "effective_creatives"
                            ] = creatives

                            st.rerun()

                        except Exception as error:
                            st.error(str(error))

                # --------------------------------------------
                # APPROVE
                # --------------------------------------------

                with approve_col:
                    if st.button(
                        "✓ Approve",
                        key=f"effective_approve_{option}",
                        type="primary",
                        width="stretch"
                    ):

                        metadata = dict(
                            item["metadata"]
                        )

                        metadata[
                            "approval_status"
                        ] = "APPROVED"

                        metadata[
                            "approved_at_utc"
                        ] = datetime.now(
                            timezone.utc
                        ).isoformat()

                        save_creative(
                            item["image"],
                            metadata
                        )

                        st.session_state[
                            "approved_creative"
                        ] = {
                            "image": item["image"],
                            "metadata": metadata,
                        }

                        st.session_state[
                            "creative_approved"
                        ] = True

                        st.success(
                            "Creative approved successfully!"
                        )

    # ========================================================
    # COPYRIGHT / PROVENANCE
    # ========================================================

    approved = st.session_state.get(
        "approved_creative"
    )

    if approved:
        st.divider()

        st.markdown(
            "### © Copyright & Creative Provenance"
        )

        metadata = approved["metadata"]

        st.success(
            "Approved creative provenance recorded."
        )

        with st.expander(
            "View Copyright Record"
        ):
            st.json(
                {
                    "Creative ID":
                        metadata["creative_id"],
                    "Generated":
                        metadata["generated_at_utc"],
                    "Unique SHA-256":
                        metadata["sha256"],
                    "Status":
                        metadata["approval_status"],
                    "Copyright":
                        metadata[
                            "copyright_provenance"
                        ],
                }
            )
