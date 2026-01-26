import re
from typing import Dict, List, Tuple

import streamlit as st


MEDIUM_OPTIONS = [
    "cpc",
    "paid_social",
    "email",
    "whatsapp",
    "push",
    "sms",
    "display",
    "referral",
    "organic",
    "affiliate",
    "social",
    "video",
    "other",
]

PRODUCT_OPTIONS = [
    "CUENTA DE AHORROS",
    "CUENTA MAS",
    "CUENTA MAXIMA",
    "BANKARD",
    "CDP",
    "CUENTA CORRIENTE",
    "CREDIMAX",
    "CUENTA NOMINA",
    "PAGO DE SERVICIOS",
    "OTRO",
]

PRODUCT_MAP: Dict[str, str] = {
    "CUENTA DE AHORROS": "CTA-AHORROS",
    "CUENTA MAS": "CTA-MAS",
    "CUENTA MAXIMA": "CTA-MAXIMA",
    "BANKARD": "BANKARD",
    "CDP": "CDP",
    "CUENTA CORRIENTE": "CTA-CORRIENTE",
    "CREDIMAX": "CREDIMAX",
    "CUENTA NOMINA": "CTA-NOMINA",
    "PAGO DE SERVICIOS": "PAGO_SERVICIOS",
}


def sanitize(value: str) -> str:
    """Sanitize UTM values using simple, consistent rules."""
    if value is None:
        return ""
    value = value.strip()
    value = re.sub(r"\s+", "_", value)
    return value


def normalize_product_label(value: str) -> str:
    """Normalize product labels for matching."""
    if value is None:
        return ""
    value = value.strip()
    value = re.sub(r"\s+", " ", value)
    return value.upper()


def resolve_product_value(selected: str, other_value: str) -> str:
    """Return standardized product code or a sanitized fallback."""
    normalized = normalize_product_label(selected)
    if normalized == "OTRO":
        return sanitize(other_value)
    mapped = PRODUCT_MAP.get(normalized)
    if mapped:
        return mapped
    return sanitize(other_value)


def append_query_params(url: str, params: List[Tuple[str, str]]) -> str:
    """Append query parameters respecting separators and edge cases."""
    if not params:
        return url

    if "?" in url:
        joiner = "" if url.endswith("?") or url.endswith("&") else "&"
    else:
        joiner = "" if url.endswith("?") or url.endswith("&") else "?"

    query = "&".join([f"{key}={value}" for key, value in params])
    return f"{url}{joiner}{query}"


def build_params(
    source: str,
    medium: str,
    campaign: str,
    content: str,
    testing: str,
    product: str,
) -> List[Tuple[str, str]]:
    """Build ordered query parameters, excluding empty values."""
    params: List[Tuple[str, str]] = []
    if source:
        params.append(("utm_source", source))
    if medium:
        params.append(("utm_medium", medium))
    if campaign:
        params.append(("utm_campaign", campaign))
    if content:
        params.append(("utm_content", content))
    if testing:
        params.append(("utm_testing", testing))
    if product:
        params.append(("utm_product", product))
    return params


def load_test_case(base_url: str) -> None:
    """Load a test case into session state."""
    st.session_state["base_url"] = base_url
    st.session_state["utm_source"] = "google"
    st.session_state["utm_medium_allow_empty"] = False
    st.session_state["utm_medium_choice"] = "cpc"
    st.session_state["utm_medium_other"] = ""
    st.session_state["utm_campaign_allow_empty"] = False
    st.session_state["utm_campaign"] = "lanzamiento_enero"
    st.session_state["utm_content"] = "banner_a"
    st.session_state["utm_testing"] = "test_a"
    st.session_state["utm_product_choice"] = "CUENTA DE AHORROS"
    st.session_state["utm_product_other"] = ""


st.set_page_config(page_title="UTM Builder", layout="centered")
st.title("UTM Builder")
st.write(
    "Construye una URL final con parametros UTM ordenados y estandarizados."
)

DEFAULTS = {
    "base_url": "",
    "utm_source": "",
    "utm_medium_allow_empty": False,
    "utm_medium_choice": MEDIUM_OPTIONS[0],
    "utm_medium_other": "",
    "utm_campaign_allow_empty": False,
    "utm_campaign": "",
    "utm_content": "",
    "utm_testing": "",
    "utm_product_choice": PRODUCT_OPTIONS[0],
    "utm_product_other": "",
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

with st.sidebar:
    st.header("Inputs")
    st.text_input("URL base (obligatorio)", key="base_url")

    st.text_input("utm_source (opcional)", key="utm_source")

    st.subheader("utm_medium")
    st.toggle(
        "Permitir vacio en utm_medium", key="utm_medium_allow_empty"
    )
    medium_options = (
        [""] + MEDIUM_OPTIONS
        if st.session_state["utm_medium_allow_empty"]
        else MEDIUM_OPTIONS
    )
    if st.session_state.get("utm_medium_choice") not in medium_options:
        st.session_state["utm_medium_choice"] = medium_options[0]
    st.selectbox(
        "utm_medium",
        options=medium_options,
        key="utm_medium_choice",
        format_func=lambda value: "-- vacio --" if value == "" else value,
    )
    if st.session_state["utm_medium_choice"] == "other":
        st.text_input("utm_medium (otro)", key="utm_medium_other")

    st.subheader("utm_campaign")
    st.toggle(
        "Permitir vacio en utm_campaign", key="utm_campaign_allow_empty"
    )
    st.text_input("utm_campaign", key="utm_campaign")

    st.text_input("utm_content (opcional)", key="utm_content")
    st.text_input("utm_testing (opcional)", key="utm_testing")

    st.subheader("utm_product")
    st.selectbox(
        "utm_product", options=PRODUCT_OPTIONS, key="utm_product_choice"
    )
    if normalize_product_label(st.session_state["utm_product_choice"]) == "OTRO":
        st.text_input("utm_product (otro)", key="utm_product_other")


base_url = st.session_state["base_url"].strip()
source = sanitize(st.session_state["utm_source"])

medium_choice = st.session_state["utm_medium_choice"]
if medium_choice == "other":
    medium_raw = st.session_state["utm_medium_other"]
elif medium_choice == "":
    medium_raw = ""
else:
    medium_raw = medium_choice
medium = sanitize(medium_raw)

campaign = sanitize(st.session_state["utm_campaign"])
content = sanitize(st.session_state["utm_content"])
testing = sanitize(st.session_state["utm_testing"])

product = resolve_product_value(
    st.session_state["utm_product_choice"],
    st.session_state["utm_product_other"],
)

errors: List[str] = []
if not base_url:
    errors.append("La URL base es obligatoria.")

if not st.session_state["utm_medium_allow_empty"] and not medium:
    errors.append("utm_medium es obligatorio. Activa 'Permitir vacio' para omitirlo.")

if not st.session_state["utm_campaign_allow_empty"] and not campaign:
    errors.append(
        "utm_campaign es obligatorio. Activa 'Permitir vacio' para omitirlo."
    )

if base_url and not (
    base_url.startswith("http://") or base_url.startswith("https://")
):
    st.warning("La URL base no parece valida (falta http:// o https://).")

if errors:
    for error in errors:
        st.error(error)

params = build_params(source, medium, campaign, content, testing, product)
final_url = "" if errors else append_query_params(base_url, params)

st.subheader("URL final")
st.text_area(
    "Copia la URL final desde aqui",
    value=final_url,
    height=120,
    help="Se construye cuando los campos obligatorios estan completos.",
)

if final_url:
    st.code(final_url)

st.subheader("Vista previa de parametros")
if params:
    st.table(
        [{"Parametro": key, "Valor": value} for key, value in params]
    )
else:
    st.info("No hay parametros para mostrar.")

with st.expander("Casos de prueba"):
    st.write(
        "Carga ejemplos rapidos para validar la logica de separadores."
    )
    st.button(
        "URL sin ?",
        on_click=load_test_case,
        args=("https://dominio.com/landing",),
        key="case_no_query",
    )
    st.button(
        "URL con ?",
        on_click=load_test_case,
        args=("https://dominio.com/landing?ref=123",),
        key="case_with_query",
    )
    st.button(
        "URL terminando en ?",
        on_click=load_test_case,
        args=("https://dominio.com/landing?",),
        key="case_trailing_q",
    )
    st.button(
        "URL terminando en &",
        on_click=load_test_case,
        args=("https://dominio.com/landing?ref=123&",),
        key="case_trailing_amp",
    )

