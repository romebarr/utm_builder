import re
from typing import Dict, List, Tuple

import streamlit as st


SOURCE_OPTIONS = [
    "Latinia",
    "Meta",
    "Google Ads",
    "Hubspot",
    "SMS",
    "Whatsapp",
    "Otro",
]

MEDIUM_OPTIONS = [
    "paid",
    "email",
    "whatsapp",
    "push",
    "sms",
    "display",
    "blog",
    "youtube",
    "banner",
]

LINK_TYPE_OPTIONS = ["Sitio web", "Deeplink", "Onboarding No Clientes"]

STAGE_MAP: Dict[str, str] = {
    "ADQUISICION": "ADQ",
    "DESARROLLO": "DES",
    "RETENCION": "RET",
    "ACTIVACION": "ACT",
}

FUNNEL_OPTIONS: Dict[str, str] = {
    "AWARENESS": "AWA",
    "CONSIDERACION": "CONS",
    "CONVERSION": "CONV",
}

OBJECTIVE_OPTIONS = [
    "APERTURA",
    "ACEPTACION",
    "OPERACION",
    "TRAFICO",
    "ALCANCE",
]

MONTH_MAP: Dict[str, str] = {
    "ENERO": "01",
    "FEBRERO": "02",
    "MARZO": "03",
    "ABRIL": "04",
    "MAYO": "05",
    "JUNIO": "06",
    "JULIO": "07",
    "AGOSTO": "08",
    "SEPTIEMBRE": "09",
    "OCTUBRE": "10",
    "NOVIEMBRE": "11",
    "DICIEMBRE": "12",
}

DEEPLINKS = [
    {
        "service": "ACTCV",
        "description": "Activacion de Clave Virtual",
        "url": "https://mercadeo.bolivariano.com/index.html?dlop=ACTCV",
    },
    {
        "service": "ACTDATOS",
        "description": "Actualizacion de Datos",
        "url": "https://mercadeo.bolivariano.com/index.html?dlop=ACTDATOS",
    },
    {
        "service": "AVAEFE",
        "description": "Avance en efectivo",
        "url": "https://mercadeo.bolivariano.com/index.html?dlop=AVAEFE",
    },
    {
        "service": "CTARD",
        "description": "Compra con tarjeta",
        "url": "https://mercadeo.bolivariano.com/index.html?dlop=CTARD",
    },
    {
        "service": "CTAID",
        "description": "Compra con tarjeta Internacional",
        "url": "https://mercadeo.bolivariano.com/index.html?dlop=CTAID",
    },
    {
        "service": "SERVICC",
        "description": "Consola de Pago Servicios",
        "url": "https://mercadeo.bolivariano.com/index.html?dlop=SERVICC",
    },
    {
        "service": "CONIN",
        "description": "Consumo por Internet",
        "url": "https://mercadeo.bolivariano.com/index.html?dlop=CONIN",
    },
    {
        "service": "DESTC",
        "description": "Desbloqueo de TC autogestion",
        "url": "https://mercadeo.bolivariano.com/index.html?dlop=DESTC",
    },
    {
        "service": "DESUSR",
        "description": "Desbloqueo de usuario",
        "url": "https://mercadeo.bolivariano.com/index.html?dlop=DESUSR",
    },
    {
        "service": "DESTD",
        "description": "Desbloqueo temporal TD autogestion",
        "url": "https://mercadeo.bolivariano.com/index.html?dlop=DESTD",
    },
    {
        "service": "DIFCO",
        "description": "Diferimiento de Consumo y avance",
        "url": "https://mercadeo.bolivariano.com/index.html?dlop=DIFCO",
    },
    {
        "service": "DIFSAL",
        "description": "Diferimiento de saldos",
        "url": "https://mercadeo.bolivariano.com/index.html?dlop=DIFSAL",
    },
    {
        "service": "PAUTPEA",
        "description": "Flujo pago servicios Automotores y Peatones",
        "url": "https://mercadeo.bolivariano.com/index.html?dlop=PAUTPEA",
    },
    {
        "service": "IMPOBLI",
        "description": "Flujo pago servicios Impuestos y obligaciones",
        "url": "https://mercadeo.bolivariano.com/index.html?dlop=IMPOBLI",
    },
    {
        "service": "PTLFCEL",
        "description": "Flujo pago servicios Telefonia Celular",
        "url": "https://mercadeo.bolivariano.com/index.html?dlop=PTLFCEL",
    },
    {
        "service": "LOGIN",
        "description": "Ingreso a la app",
        "url": "https://mercadeo.bolivariano.com/index.html?dlop=LOGIN",
    },
    {
        "service": "MATRPS",
        "description": "Matriculacion Pago de Servicios",
        "url": "https://mercadeo.bolivariano.com/index.html?dlop=MATRPS&servicio=",
    },
    {
        "service": "OPENACOUNT",
        "description": "ONB Apertura de Cuenta",
        "url": "https://mercadeo.bolivariano.com/index.html?dlop=OPENACOUNT",
    },
    {
        "service": "CRTDEPOL",
        "description": "ONB Certificado de deposito online",
        "url": "https://mercadeo.bolivariano.com/index.html?dlop=CRTDEPOL",
    },
    {
        "service": "CREDIMAX",
        "description": "ONB Credimax Online",
        "url": "https://mercadeo.bolivariano.com/index.html?dlop=CREDIMAX",
    },
    {
        "service": "CTAMASON",
        "description": "ONB Cuenta Mas Online",
        "url": "https://mercadeo.bolivariano.com/index.html?dlop=CTAMASON",
    },
    {
        "service": "CTAMAXON",
        "description": "ONB Cuenta Maxima Online",
        "url": "https://mercadeo.bolivariano.com/index.html?dlop=CTAMAXON",
    },
    {
        "service": "REFBANCA",
        "description": "ONB Referencia Bancaria",
        "url": "https://mercadeo.bolivariano.com/index.html?dlop=REFBANCA",
    },
    {
        "service": "SOLPRO",
        "description": "ONB Solicitud de productos",
        "url": "https://mercadeo.bolivariano.com/index.html?dlop=SOLPRO",
    },
    {
        "service": "TARBKN",
        "description": "ONB Tarjeta de credito cliente",
        "url": "https://mercadeo.bolivariano.com/index.html?dlop=TARBKN",
    },
    {
        "service": "PEDUCA",
        "description": "Pagar Educacion",
        "url": "https://mercadeo.bolivariano.com/index.html?dlop=PEDUCA",
    },
    {
        "service": "PAGUA",
        "description": "Pagar el agua",
        "url": "https://mercadeo.bolivariano.com/index.html?dlop=PAGUA",
    },
    {
        "service": "PINNET",
        "description": "Pagar el internet",
        "url": "https://mercadeo.bolivariano.com/index.html?dlop=PINNET",
    },
    {
        "service": "PIESS",
        "description": "Pagar IESS",
        "url": "https://mercadeo.bolivariano.com/index.html?dlop=PIESS",
    },
    {
        "service": "PLUZ",
        "description": "Pagar la luz",
        "url": "https://mercadeo.bolivariano.com/index.html?dlop=PLUZ",
    },
    {
        "service": "PTRJCA",
        "description": "Pagar Tarjetas comerciales",
        "url": "https://mercadeo.bolivariano.com/index.html?dlop=PTRJCA",
    },
    {
        "service": "PTLFIJA",
        "description": "Pagar telefonia fija",
        "url": "https://mercadeo.bolivariano.com/index.html?dlop=PTLFIJA",
    },
    {
        "service": "PTVPAG",
        "description": "Pagar Television pagada",
        "url": "https://mercadeo.bolivariano.com/index.html?dlop=PTVPAG",
    },
    {
        "service": "SCOREC",
        "description": "Score Crediticio",
        "url": "https://mercadeo.bolivariano.com/index.html?dlop=SCOREC",
    },
    {
        "service": "TRFWIP",
        "description": "WIP",
        "url": "https://mercadeo.bolivariano.com/index.html?dlop=TRFWIP",
    },
    {
        "service": "AGUA",
        "description": "Matriculacion de Agua",
        "url": "https://mercadeo.bolivariano.com/index.html?dlop=AGUA",
    },
    {
        "service": "INTERNET",
        "description": "Matriculacion de Internet",
        "url": "https://mercadeo.bolivariano.com/index.html?dlop=INTERNET",
    },
    {
        "service": "LUZ",
        "description": "Matriculacion de Luz",
        "url": "https://mercadeo.bolivariano.com/index.html?dlop=LUZ",
    },
    {
        "service": "TELEFONIA_CELULAR",
        "description": "Matriculacion de Telefonia Celular",
        "url": "https://mercadeo.bolivariano.com/index.html?dlop=TELEFONIA_CELULAR",
    },
    {
        "service": "TELEFONIA_FIJA",
        "description": "Matriculacion de Telefonia Fija",
        "url": "https://mercadeo.bolivariano.com/index.html?dlop=TELEFONIA_FIJA",
    },
    {
        "service": "TELEVISION_PAGADA",
        "description": "Matriculacion de Television Pagada",
        "url": "https://mercadeo.bolivariano.com/index.html?dlop=TELEVISION_PAGADA",
    },
    {
        "service": "EDUCACION",
        "description": "Matriculacion de Educacion",
        "url": "https://mercadeo.bolivariano.com/index.html?dlop=EDUCACION",
    },
    {
        "service": "AUTOMOTORES_PEATONES",
        "description": "Matriculacion de Automotores y Peatones",
        "url": "https://mercadeo.bolivariano.com/index.html?dlop=AUTOMOTORES_PEATONES",
    },
    {
        "service": "CASAS_TARJETAS_COMERCIALES",
        "description": "Matriculacion de Tarjetas Comerciales",
        "url": "https://mercadeo.bolivariano.com/index.html?dlop=CASAS_TARJETAS_COMERCIALES",
    },
    {
        "service": "IMPUESTOS_OBLIGACIONES",
        "description": "Matriculacion de Impuestos y Obligaciones",
        "url": "https://mercadeo.bolivariano.com/index.html?dlop=IMPUESTOS_OBLIGACIONES",
    },
    {
        "service": "PAGO_ADUANA",
        "description": "Matriculacion de Servicios Aduaneros",
        "url": "https://mercadeo.bolivariano.com/index.html?dlop=PAGO_ADUANA",
    },
    {
        "service": "SALUD",
        "description": "Matriculacion de Salud",
        "url": "https://mercadeo.bolivariano.com/index.html?dlop=SALUD",
    },
    {
        "service": "OTROS",
        "description": "Matriculacion de Otros",
        "url": "https://mercadeo.bolivariano.com/index.html?dlop=OTROS",
    },
]

DEEPLINK_MAP = {item["service"]: item for item in DEEPLINKS}

ONBOARDING_LINKS: Dict[str, str] = {
    "Credimax": "https://credimax.bolivariano.com/",
    "Tarjeta de Credito": "https://tarjetadecredito.bolivariano.com/",
    "Cuenta de Ahorros": "https://cuentas.bolivariano.com/",
}

PRODUCT_OPTIONS = [
    "CUENTA DE AHORROS",
    "CUENTA MAS",
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


def normalize_year(value: str) -> str:
    """Normalize year to last two digits."""
    if value is None:
        return ""
    digits = re.sub(r"\D", "", value.strip())
    if len(digits) < 2:
        return ""
    return digits[-2:]


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


def build_campaign_name(
    stage: str,
    funnel: str,
    product: str,
    objective: str,
    tipo: str,
    mes: str,
    anio: str,
) -> str:
    """Build utm_campaign name using the required nomenclature."""
    required_parts = [
        sanitize(stage),
        sanitize(funnel),
        sanitize(product),
        sanitize(objective),
        sanitize(mes),
        sanitize(anio),
    ]
    if any(not part for part in required_parts):
        return ""
    optional_tipo = sanitize(tipo)
    parts = [
        sanitize(stage),
        sanitize(funnel),
        sanitize(product),
        sanitize(objective),
    ]
    if optional_tipo:
        parts.append(optional_tipo)
    parts.extend([sanitize(mes), sanitize(anio)])
    return "_".join(parts)


def load_test_case(base_url: str) -> None:
    """Load a test case into session state."""
    st.session_state["link_type"] = "Sitio web"
    st.session_state["base_url"] = base_url
    st.session_state["utm_source_choice"] = SOURCE_OPTIONS[0]
    st.session_state["utm_source_other"] = ""
    st.session_state["utm_medium_choice"] = "paid"
    st.session_state["utm_medium_other"] = ""
    st.session_state["utm_campaign_use_builder"] = False
    st.session_state["utm_campaign"] = "lanzamiento_enero"
    st.session_state["utm_campaign_stage"] = list(STAGE_MAP.keys())[0]
    st.session_state["utm_campaign_funnel"] = list(FUNNEL_OPTIONS.keys())[0]
    st.session_state["utm_campaign_objective"] = OBJECTIVE_OPTIONS[0]
    st.session_state["utm_campaign_tipo"] = "PROMO"
    st.session_state["utm_campaign_mes"] = "ENERO"
    st.session_state["utm_campaign_anio"] = "2026"
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
    "link_type": "Sitio web",
    "base_url": "",
    "deeplink_choice": DEEPLINKS[0]["service"],
    "deeplink_servicio": "",
    "onboarding_choice": list(ONBOARDING_LINKS.keys())[0],
    "utm_source_choice": SOURCE_OPTIONS[0],
    "utm_source_other": "",
    "utm_medium_choice": MEDIUM_OPTIONS[0],
    "utm_medium_other": "",
    "utm_campaign_use_builder": False,
    "utm_campaign": "",
    "utm_campaign_stage": list(STAGE_MAP.keys())[0],
    "utm_campaign_funnel": list(FUNNEL_OPTIONS.keys())[0],
    "utm_campaign_objective": OBJECTIVE_OPTIONS[0],
    "utm_campaign_tipo": "",
    "utm_campaign_mes": "",
    "utm_campaign_anio": "",
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
    st.selectbox(
        "Tipo de enlace",
        options=LINK_TYPE_OPTIONS,
        key="link_type",
    )
    if st.session_state["link_type"] == "Sitio web":
        st.text_input("URL base (obligatorio)", key="base_url")
    elif st.session_state["link_type"] == "Deeplink":
        st.selectbox(
            "Servicio deeplink",
            options=[item["service"] for item in DEEPLINKS],
            key="deeplink_choice",
            format_func=lambda value: (
                f"{DEEPLINK_MAP[value]['description']} ({value})"
            ),
        )
        if st.session_state["deeplink_choice"] == "MATRPS":
            st.text_input("servicio (opcional)", key="deeplink_servicio")
        selected_url = DEEPLINK_MAP[
            st.session_state["deeplink_choice"]
        ]["url"]
        if (
            st.session_state["deeplink_choice"] == "MATRPS"
            and sanitize(st.session_state["deeplink_servicio"])
        ):
            selected_url += sanitize(st.session_state["deeplink_servicio"])
        st.session_state["base_url"] = selected_url
        st.text_input(
            "URL base (deeplink)",
            value=selected_url,
            disabled=True,
        )
    else:
        st.selectbox(
            "Onboarding no clientes",
            options=list(ONBOARDING_LINKS.keys()),
            key="onboarding_choice",
        )
        selected_url = ONBOARDING_LINKS[
            st.session_state["onboarding_choice"]
        ]
        st.session_state["base_url"] = selected_url
        st.text_input(
            "URL base (onboarding)",
            value=selected_url,
            disabled=True,
        )

    st.selectbox(
        "utm_source (obligatorio)",
        options=SOURCE_OPTIONS,
        key="utm_source_choice",
    )
    if st.session_state["utm_source_choice"] == "Otro":
        st.text_input("utm_source (otro)", key="utm_source_other")

    st.subheader("utm_medium")
    medium_options = MEDIUM_OPTIONS
    if st.session_state.get("utm_medium_choice") not in medium_options:
        st.session_state["utm_medium_choice"] = medium_options[0]
    st.selectbox(
        "utm_medium",
        options=medium_options,
        key="utm_medium_choice",
    )
    if st.session_state["utm_medium_choice"] == "Otro":
        st.text_input("utm_medium (otro)", key="utm_medium_other")

    st.subheader("utm_campaign")
    st.toggle(
        "Generar utm_campaign", key="utm_campaign_use_builder"
    )
    if st.session_state["utm_campaign_use_builder"]:
        st.selectbox(
            "Etapa",
            options=list(STAGE_MAP.keys()),
            key="utm_campaign_stage",
        )
        st.selectbox(
            "Funnel",
            options=list(FUNNEL_OPTIONS.keys()),
            key="utm_campaign_funnel",
        )
        st.selectbox(
            "Objetivo",
            options=OBJECTIVE_OPTIONS,
            key="utm_campaign_objective",
        )
        st.text_input("Tipo (opcional)", key="utm_campaign_tipo")
        st.selectbox(
            "Mes",
            options=[""] + list(MONTH_MAP.keys()),
            key="utm_campaign_mes",
            format_func=lambda value: "Selecciona" if value == "" else value,
        )
        st.text_input("Anio", key="utm_campaign_anio")
    else:
        st.text_input("utm_campaign", key="utm_campaign")

    st.text_input("utm_content (obligatorio)", key="utm_content")
    st.text_input("utm_testing (opcional)", key="utm_testing")

    st.subheader("utm_product")
    st.selectbox(
        "utm_product", options=PRODUCT_OPTIONS, key="utm_product_choice"
    )
    if normalize_product_label(st.session_state["utm_product_choice"]) == "OTRO":
        st.text_input("utm_product (otro)", key="utm_product_other")


if st.session_state["link_type"] == "Deeplink":
    base_url = DEEPLINK_MAP[st.session_state["deeplink_choice"]]["url"]
    if st.session_state["deeplink_choice"] == "MATRPS":
        base_url += sanitize(st.session_state["deeplink_servicio"])
elif st.session_state["link_type"] == "Onboarding No Clientes":
    base_url = ONBOARDING_LINKS[st.session_state["onboarding_choice"]]
else:
    base_url = st.session_state["base_url"].strip()
if st.session_state["utm_source_choice"] == "Otro":
    source = sanitize(st.session_state["utm_source_other"])
else:
    source = sanitize(st.session_state["utm_source_choice"])

medium_choice = st.session_state["utm_medium_choice"]
if medium_choice == "Otro":
    medium = sanitize(st.session_state["utm_medium_other"])
else:
    medium = sanitize(medium_choice)

product = resolve_product_value(
    st.session_state["utm_product_choice"],
    st.session_state["utm_product_other"],
)

if st.session_state["utm_campaign_use_builder"]:
    stage_value = STAGE_MAP.get(st.session_state["utm_campaign_stage"], "")
    funnel_value = FUNNEL_OPTIONS.get(
        st.session_state["utm_campaign_funnel"], ""
    )
    month_value = MONTH_MAP.get(st.session_state["utm_campaign_mes"], "")
    year_value = normalize_year(st.session_state["utm_campaign_anio"])
    campaign = build_campaign_name(
        stage_value,
        funnel_value,
        product,
        st.session_state["utm_campaign_objective"],
        st.session_state["utm_campaign_tipo"],
        month_value,
        year_value,
    )
else:
    campaign = sanitize(st.session_state["utm_campaign"])
content = sanitize(st.session_state["utm_content"])
testing = sanitize(st.session_state["utm_testing"])

errors: List[str] = []
if not base_url:
    errors.append("La URL base es obligatoria.")

if not source:
    errors.append("utm_source es obligatorio.")

if not medium:
    errors.append("utm_medium es obligatorio.")

if not content:
    errors.append("utm_content es obligatorio.")

if not campaign:
    errors.append("utm_campaign es obligatorio.")

if not product:
    errors.append("utm_product es obligatorio.")

if st.session_state["utm_campaign_use_builder"]:
    missing_fields = []
    if not STAGE_MAP.get(st.session_state["utm_campaign_stage"], ""):
        missing_fields.append("Etapa")
    if not FUNNEL_OPTIONS.get(st.session_state["utm_campaign_funnel"], ""):
        missing_fields.append("Funnel")
    if not sanitize(st.session_state["utm_campaign_objective"]):
        missing_fields.append("Objetivo")
    if not MONTH_MAP.get(st.session_state["utm_campaign_mes"], ""):
        missing_fields.append("Mes")
    if not normalize_year(st.session_state["utm_campaign_anio"]):
        missing_fields.append("Anio")
    if missing_fields:
        errors.append(
            "Faltan campos para generar utm_campaign: "
            + ", ".join(missing_fields)
            + "."
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

if st.session_state["utm_campaign_use_builder"]:
    st.subheader("utm_campaign generado")
    st.text_input(
        "Valor generado",
        value=campaign,
        disabled=True,
        help="Se usa este valor en la URL final.",
    )

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

