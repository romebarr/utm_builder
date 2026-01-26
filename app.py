import re
from urllib.parse import quote

import streamlit as st


UTM_MEDIUM_OPTIONS: list[str] = [
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

UTM_PRODUCT_OPTIONS: list[str] = [
    "CUENTA DE AHORROS",
    "CUENTA MAS",
    "CUENTA MAXIMA",
    "BANKARD",
    "CUENTA CORRIENTE",
    "CREDIMAX",
    "CUENTA NOMINA",
    "PAGO DE SERVICIOS",
    "OTRO",
]

UTM_PRODUCT_MAP: dict[str, str] = {
    "CUENTA DE AHORROS": "CTA-AHORROS",
    "CUENTA MAS": "CTA-MAS",
    "CUENTA MAXIMA": "CTA-MAXIMA",
    "BANKARD": "BANKARD",
    "CUENTA CORRIENTE": "CTA-CORRIENTE",
    "CREDIMAX": "CREDIMAX",
    "CUENTA NOMINA": "CTA-NOMINA",
    "PAGO DE SERVICIOS": "PAGO_SERVICIOS",
}


def sanitize(value: str) -> str:
    """Normalize a UTM value: trim, spaces -> underscores, allow empty."""
    cleaned = value.strip()
    cleaned = re.sub(r"\s+", "_", cleaned)
    return cleaned if cleaned else ""


def normalize_product_key(value: str) -> str:
    """Normalize utm_product label before mapping (trim, collapse spaces, uppercase)."""
    collapsed = re.sub(r"\s+", " ", value.strip())
    return collapsed.upper()


def standardize_utm_product(selected_label: str, other_value: str) -> str:
    """Return standardized utm_product code or sanitized fallback when OTRO."""
    key = normalize_product_key(selected_label)
    if key != "OTRO" and key in UTM_PRODUCT_MAP:
        return UTM_PRODUCT_MAP[key]
    return sanitize(other_value)


def looks_like_url(value: str) -> bool:
    """Very small URL heuristic: starts with http:// or https://."""
    v = value.strip().lower()
    return v.startswith("http://") or v.startswith("https://")


def append_query_params(url: str, params: list[tuple[str, str]]) -> str:
    """
    Append already-filtered query params to a URL with correct separators.

    Rules:
    - If URL contains '?', first param uses '&', otherwise uses '?'.
    - If URL ends with '?' or '&', don't duplicate separators.
    """
    base = url.strip()
    if not base or not params:
        return base

    encoded_pairs: list[str] = []
    for k, v in params:
        if not k:
            continue
        encoded_v = quote(v, safe="-_.~_")
        encoded_pairs.append(f"{k}={encoded_v}")

    if not encoded_pairs:
        return base

    if base.endswith("?") or base.endswith("&"):
        connector = ""
    else:
        connector = "&" if "?" in base else "?"

    return base + connector + "&".join(encoded_pairs)


def build_utm_params(
    utm_source: str,
    utm_medium: str,
    utm_campaign: str,
    utm_content: str,
    utm_testing: str,
    utm_product: str,
) -> list[tuple[str, str]]:
    """Build ordered list of UTM params, excluding empty values."""
    ordered: list[tuple[str, str]] = [
        ("utm_source", utm_source),
        ("utm_medium", utm_medium),
        ("utm_campaign", utm_campaign),
        ("utm_content", utm_content),
        ("utm_testing", utm_testing),
        ("utm_product", utm_product),
    ]
    return [(k, v) for (k, v) in ordered if v]


def _set_case(case: dict[str, str]) -> None:
    """Load a test case into Streamlit session_state."""
    for k, v in case.items():
        st.session_state[k] = v


def main() -> None:
    st.set_page_config(page_title="UTM Builder", page_icon="🔗", layout="centered")
    st.title("UTM Builder")
    st.caption("Construye una URL final agregando parámetros UTM en el orden correcto.")

    with st.expander("Casos de prueba", expanded=False):
        st.write("Carga un ejemplo al formulario para validar separadores `?` vs `&`.")

        col1, col2 = st.columns(2)
        with col1:
            st.button(
                "URL sin ?",
                use_container_width=True,
                on_click=_set_case,
                args=(
                    {
                        "base_url": "https://dominio.com/landing",
                        "utm_source": "google",
                        "utm_medium_choice": "cpc",
                        "utm_medium_other": "",
                        "allow_empty_medium": False,
                        "utm_campaign": "promo_enero",
                        "allow_empty_campaign": False,
                        "utm_content": "banner_1",
                        "utm_testing": "ab_test_a",
                        "utm_product_choice": "CUENTA DE AHORROS",
                        "utm_product_other": "",
                    },
                ),
            )
            st.button(
                "URL terminando en ?",
                use_container_width=True,
                on_click=_set_case,
                args=(
                    {
                        "base_url": "https://dominio.com/landing?",
                        "utm_source": "meta",
                        "utm_medium_choice": "paid_social",
                        "utm_medium_other": "",
                        "allow_empty_medium": False,
                        "utm_campaign": "remarketing_feb",
                        "allow_empty_campaign": False,
                        "utm_content": "story_9",
                        "utm_testing": "",
                        "utm_product_choice": "OTRO",
                        "utm_product_other": "Cuenta Premium",
                    },
                ),
            )
        with col2:
            st.button(
                "URL con ? (ya tiene params)",
                use_container_width=True,
                on_click=_set_case,
                args=(
                    {
                        "base_url": "https://dominio.com/landing?ref=123",
                        "utm_source": "newsletter",
                        "utm_medium_choice": "email",
                        "utm_medium_other": "",
                        "allow_empty_medium": False,
                        "utm_campaign": "lanzamiento",
                        "allow_empty_campaign": False,
                        "utm_content": "",
                        "utm_testing": "test_01",
                        "utm_product_choice": "BANKARD",
                        "utm_product_other": "",
                    },
                ),
            )
            st.button(
                "URL terminando en &",
                use_container_width=True,
                on_click=_set_case,
                args=(
                    {
                        "base_url": "https://dominio.com/landing?ref=123&",
                        "utm_source": "whatsapp",
                        "utm_medium_choice": "whatsapp",
                        "utm_medium_other": "",
                        "allow_empty_medium": False,
                        "utm_campaign": "wpp_blast",
                        "allow_empty_campaign": False,
                        "utm_content": "",
                        "utm_testing": "",
                        "utm_product_choice": "PAGO DE SERVICIOS",
                        "utm_product_other": "",
                    },
                ),
            )

    st.divider()

    with st.sidebar:
        st.header("Inputs")

        base_url = st.text_input(
            "URL base (obligatorio)",
            key="base_url",
            placeholder="https://dominio.com/landing",
        )

        utm_source_raw = st.text_input("utm_source (opcional)", key="utm_source")

        allow_empty_medium = st.toggle(
            "Permitir vacío en utm_medium",
            value=st.session_state.get("allow_empty_medium", False),
            key="allow_empty_medium",
        )

        medium_choices = list(UTM_MEDIUM_OPTIONS)
        if allow_empty_medium:
            medium_choices = [""] + medium_choices

        utm_medium_choice = st.selectbox(
            "utm_medium (recomendado)",
            options=medium_choices,
            index=0 if allow_empty_medium else medium_choices.index("cpc"),
            key="utm_medium_choice",
            help="Si eliges 'other', se habilita un input libre.",
        )
        utm_medium_other = ""
        if utm_medium_choice == "other":
            utm_medium_other = st.text_input(
                "utm_medium (otro - input libre)",
                key="utm_medium_other",
                placeholder="ej: partners",
            )
        else:
            st.session_state["utm_medium_other"] = st.session_state.get("utm_medium_other", "")

        allow_empty_campaign = st.toggle(
            "Permitir vacío en utm_campaign",
            value=st.session_state.get("allow_empty_campaign", False),
            key="allow_empty_campaign",
        )
        utm_campaign_raw = st.text_input("utm_campaign", key="utm_campaign")

        utm_content_raw = st.text_input("utm_content (opcional)", key="utm_content")
        utm_testing_raw = st.text_input("utm_testing (opcional)", key="utm_testing")

        utm_product_choice = st.selectbox(
            "utm_product",
            options=UTM_PRODUCT_OPTIONS,
            key="utm_product_choice",
        )
        utm_product_other = ""
        if normalize_product_key(utm_product_choice) == "OTRO":
            utm_product_other = st.text_input(
                "utm_product (otro - input libre)",
                key="utm_product_other",
                placeholder="ej: Mi Producto",
            )
        else:
            st.session_state["utm_product_other"] = st.session_state.get("utm_product_other", "")

    errors: list[str] = []

    if not base_url.strip():
        errors.append("La URL base es obligatoria.")

    if base_url.strip() and not looks_like_url(base_url):
        st.warning("La URL no parece válida (debería empezar con http:// o https://). Puedes continuar.")

    utm_source = sanitize(utm_source_raw)

    if utm_medium_choice == "other":
        utm_medium = sanitize(utm_medium_other)
    else:
        utm_medium = sanitize(utm_medium_choice)

    utm_campaign = sanitize(utm_campaign_raw)
    utm_content = sanitize(utm_content_raw)
    utm_testing = sanitize(utm_testing_raw)

    utm_product = standardize_utm_product(utm_product_choice, utm_product_other)

    if not allow_empty_medium and not utm_medium:
        errors.append("utm_medium no puede estar vacío (desactiva 'Permitir vacío' o completa el valor).")

    if not allow_empty_campaign and not utm_campaign:
        errors.append("utm_campaign no puede estar vacío (desactiva 'Permitir vacío' o completa el valor).")

    params = build_utm_params(
        utm_source=utm_source,
        utm_medium=utm_medium,
        utm_campaign=utm_campaign,
        utm_content=utm_content,
        utm_testing=utm_testing,
        utm_product=utm_product,
    )

    final_url = ""
    if errors:
        for e in errors:
            st.error(e)
    else:
        final_url = append_query_params(base_url, params)

    st.subheader("URL final")
    st.text_area(
        "Copia esta URL",
        value=final_url,
        height=110,
        key="final_url",
        help="Puedes seleccionar todo y copiar (Ctrl/Cmd + C).",
    )
    if final_url:
        st.code(final_url, language="text")

    st.subheader("Vista previa de parámetros")
    if params:
        st.table([{"key": k, "value": v} for (k, v) in params])
    else:
        st.info("No hay parámetros para agregar todavía.")


if __name__ == "__main__":
    main()

