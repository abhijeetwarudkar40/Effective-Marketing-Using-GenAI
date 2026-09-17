import math
import streamlit as st


def safe_value(value, default="N/A"):
    if value is None:
        return default
    try:
        if value != value:
            return default
    except Exception:
        pass

    text = str(value).strip()
    if not text or text.lower() in {"nan", "none", "null"}:
        return default
    return text


def field_value(row, column, default="N/A"):
    """Safely read a field from a pandas Series/dict."""
    if row is None:
        return default
    try:
        if column not in row.index:
            return default
        return safe_value(row[column], default)
    except Exception:
        try:
            return safe_value(row.get(column), default)
        except Exception:
            return default


def page_header(title, subtitle=None):
    st.title(title)
    if subtitle:
        st.caption(subtitle)


def section_header(title, subtitle=None):
    st.subheader(title)
    if subtitle:
        st.caption(subtitle)


def section_title(title, subtitle=None):
    section_header(title, subtitle)


def kpi_card(label, value, description=None, icon=None):
    if icon:
        st.metric(f"{icon} {label}", safe_value(value))
    else:
        st.metric(label, safe_value(value))
    if description:
        st.caption(description)


def info_card(title, value, description=None):
    with st.container(border=True):
        st.markdown(f"**{title}**")
        st.write(safe_value(value))
        if description:
            st.caption(description)


def text_card(title, content):
    with st.container(border=True):
        st.markdown(f"**{title}**")
        st.write(safe_value(content))


def badge(text, badge_type="default"):
    # Native Streamlit replacement; avoids raw HTML rendering issues.
    st.caption(f"{safe_value(text)}")


def campaign_field(label, value):
    st.markdown(f"**{label}**")
    st.write(safe_value(value))


def empty_state(message):
    st.info(message)


def inject_global_css():
    # Intentionally empty. The UI uses native Streamlit components so
    # HTML is never accidentally rendered as a code block.
    return None


def load_css():
    return inject_global_css()
