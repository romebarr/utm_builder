"""
UTM Builder - Aplicación Streamlit para construir URLs con parámetros UTM.
"""

import re
import streamlit as st
from typing import Optional

# =============================================================================
# CONSTANTES Y MAPEOS
# =============================================================================

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

UTM_PRODUCT_MAPPING: dict[str, str] = {
    "CUENTA DE AHORROS": "CTA-AHORROS",
    "CUENTA MAS": "CTA-MAS",
    "CUENTA MAXIMA": "CTA-MAXIMA",
    "BANKARD": "BANKARD",
    "CUENTA CORRIENTE": "CTA-CORRIENTE",
    "CREDIMAX": "CREDIMAX",
    "CUENTA NOMINA": "CTA-NOMINA",
    "PAGO DE SERVICIOS": "PAGO_SERVICIOS",
}

# Casos de prueba predefinidos
TEST_CASES: dict[str, dict] = {
    "URL sin ?": {
        "url": "https://dominio.com/landing",
        "utm_source": "google",
        "utm_medium": "cpc",
        "utm_campaign": "verano2024",
        "utm_content": "",
        "utm_testing": "",
        "utm_product": "CUENTA DE AHORROS",
        "utm_product_otro": "",
    },
    "URL con ?": {
        "url": "https://dominio.com/landing?ref=123",
        "utm_source": "facebook",
        "utm_medium": "paid_social",
        "utm_campaign": "promo_navidad",
        "utm_content": "banner_principal",
        "utm_testing": "",
        "utm_product": "BANKARD",
        "utm_product_otro": "",
    },
    "URL terminando en ?": {
        "url": "https://dominio.com/landing?",
        "utm_source": "newsletter",
        "utm_medium": "email",
        "utm_campaign": "bienvenida",
        "utm_content": "",
        "utm_testing": "test_a",
        "utm_product": "CREDIMAX",
        "utm_product_otro": "",
    },
    "URL terminando en &": {
        "url": "https://dominio.com/landing?ref=123&",
        "utm_source": "whatsapp",
        "utm_medium": "whatsapp",
        "utm_campaign": "referidos",
        "utm_content": "mensaje_directo",
        "utm_testing": "",
        "utm_product": "OTRO",
        "utm_product_otro": "PRODUCTO_ESPECIAL",
    },
}


# =============================================================================
# FUNCIONES PURAS
# =============================================================================


def sanitize(value: str) -> str:
    """
    Sanitiza un valor de parámetro UTM.
    
    - Elimina espacios al inicio y final
    - Reemplaza secuencias de espacios por guión bajo
    - Retorna cadena vacía si el resultado está vacío
    
    Args:
        value: El valor a sanitizar
        
    Returns:
        El valor sanitizado
    """
    if not value:
        return ""
    
    # Strip y reemplazar múltiples espacios por uno solo, luego por _
    result = value.strip()
    result = re.sub(r'\s+', '_', result)
    
    return result if result else ""


def normalize_for_mapping(value: str) -> str:
    """
    Normaliza un valor para compararlo con el mapeo de productos.
    
    - Elimina espacios al inicio y final
    - Colapsa múltiples espacios en uno
    - Convierte a mayúsculas
    
    Args:
        value: El valor a normalizar
        
    Returns:
        El valor normalizado
    """
    if not value:
        return ""
    
    result = value.strip()
    result = re.sub(r'\s+', ' ', result)
    result = result.upper()
    
    return result


def get_utm_product_value(selected_option: str, custom_value: str = "") -> str:
    """
    Obtiene el valor final de utm_product según la opción seleccionada.
    
    Si la opción está en el mapeo, retorna el código estandarizado.
    Si es "OTRO", retorna el valor personalizado sanitizado.
    
    Args:
        selected_option: La opción seleccionada del dropdown
        custom_value: El valor personalizado si se eligió "OTRO"
        
    Returns:
        El valor final de utm_product
    """
    normalized = normalize_for_mapping(selected_option)
    
    if normalized in UTM_PRODUCT_MAPPING:
        return UTM_PRODUCT_MAPPING[normalized]
    
    # Es "OTRO" o no coincide - usar valor personalizado sanitizado
    return sanitize(custom_value)


def validate_url(url: str) -> tuple[bool, Optional[str]]:
    """
    Valida que la URL sea válida.
    
    Args:
        url: La URL a validar
        
    Returns:
        Tupla (es_valida, mensaje_warning)
        - es_valida: False si está vacía
        - mensaje_warning: Advertencia si no empieza con http/https
    """
    if not url or not url.strip():
        return False, None
    
    url = url.strip()
    
    if not url.startswith(('http://', 'https://')):
        return True, "La URL no comienza con http:// o https://. Se continuará, pero verifica que sea correcta."
    
    return True, None


def append_query_params(url: str, params: list[tuple[str, str]]) -> str:
    """
    Agrega parámetros de consulta a una URL de forma correcta.
    
    Maneja correctamente los casos:
    - URL sin parámetros existentes
    - URL con parámetros existentes
    - URL terminando en ? o &
    
    Args:
        url: La URL base
        params: Lista de tuplas (nombre, valor) de parámetros
        
    Returns:
        La URL con los parámetros agregados
    """
    if not params:
        return url
    
    url = url.strip()
    
    # Construir el string de parámetros
    param_string = "&".join(f"{name}={value}" for name, value in params)
    
    # Determinar el separador correcto
    if "?" not in url:
        # No hay query string, usar ?
        return f"{url}?{param_string}"
    else:
        # Ya hay query string
        # Limpiar terminaciones problemáticas
        while url.endswith('?') or url.endswith('&'):
            url = url[:-1]
        
        # Si después de limpiar ya no tiene ?, agregar ?
        if "?" not in url:
            return f"{url}?{param_string}"
        
        # Tiene ? y contenido, agregar con &
        return f"{url}&{param_string}"


def build_utm_params(
    utm_source: str,
    utm_medium: str,
    utm_campaign: str,
    utm_content: str,
    utm_testing: str,
    utm_product: str,
) -> list[tuple[str, str]]:
    """
    Construye la lista de parámetros UTM en el orden correcto.
    
    Solo incluye parámetros que tienen valor.
    
    Args:
        utm_source: Valor de utm_source
        utm_medium: Valor de utm_medium
        utm_campaign: Valor de utm_campaign
        utm_content: Valor de utm_content
        utm_testing: Valor de utm_testing
        utm_product: Valor de utm_product
        
    Returns:
        Lista de tuplas (nombre, valor) ordenada
    """
    params = []
    
    # Orden específico requerido
    param_definitions = [
        ("utm_source", utm_source),
        ("utm_medium", utm_medium),
        ("utm_campaign", utm_campaign),
        ("utm_content", utm_content),
        ("utm_testing", utm_testing),
        ("utm_product", utm_product),
    ]
    
    for name, value in param_definitions:
        sanitized = sanitize(value) if name != "utm_product" else value
        if sanitized:
            params.append((name, sanitized))
    
    return params


def build_final_url(
    base_url: str,
    utm_source: str,
    utm_medium: str,
    utm_campaign: str,
    utm_content: str,
    utm_testing: str,
    utm_product: str,
) -> str:
    """
    Construye la URL final con todos los parámetros UTM.
    
    Args:
        base_url: La URL base
        utm_source: Valor de utm_source
        utm_medium: Valor de utm_medium
        utm_campaign: Valor de utm_campaign
        utm_content: Valor de utm_content
        utm_testing: Valor de utm_testing
        utm_product: Valor de utm_product
        
    Returns:
        La URL final con parámetros UTM
    """
    params = build_utm_params(
        utm_source, utm_medium, utm_campaign,
        utm_content, utm_testing, utm_product
    )
    
    return append_query_params(base_url, params)


# =============================================================================
# INTERFAZ DE USUARIO (STREAMLIT)
# =============================================================================


def init_session_state():
    """Inicializa el estado de la sesión con valores por defecto."""
    defaults = {
        "url_base": "",
        "utm_source": "",
        "utm_medium_index": 0,
        "utm_medium_custom": "",
        "utm_campaign": "",
        "utm_content": "",
        "utm_testing": "",
        "utm_product_index": 0,
        "utm_product_otro": "",
        "allow_empty_medium": False,
        "allow_empty_campaign": False,
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def load_test_case(case_name: str):
    """Carga un caso de prueba en el formulario."""
    case = TEST_CASES[case_name]
    
    st.session_state.url_base = case["url"]
    st.session_state.utm_source = case["utm_source"]
    st.session_state.utm_campaign = case["utm_campaign"]
    st.session_state.utm_content = case["utm_content"]
    st.session_state.utm_testing = case["utm_testing"]
    st.session_state.utm_product_otro = case["utm_product_otro"]
    
    # Encontrar índice de utm_medium
    if case["utm_medium"] in UTM_MEDIUM_OPTIONS:
        st.session_state.utm_medium_index = UTM_MEDIUM_OPTIONS.index(case["utm_medium"])
    else:
        st.session_state.utm_medium_index = UTM_MEDIUM_OPTIONS.index("other")
        st.session_state.utm_medium_custom = case["utm_medium"]
    
    # Encontrar índice de utm_product
    if case["utm_product"] in UTM_PRODUCT_OPTIONS:
        st.session_state.utm_product_index = UTM_PRODUCT_OPTIONS.index(case["utm_product"])


def render_sidebar():
    """Renderiza la barra lateral con los inputs."""
    st.sidebar.header("Parámetros UTM")
    
    # URL Base
    st.sidebar.subheader("URL Base *")
    url_base = st.sidebar.text_input(
        "URL Base",
        value=st.session_state.url_base,
        key="url_base_input",
        placeholder="https://ejemplo.com/landing",
        label_visibility="collapsed",
    )
    
    st.sidebar.divider()
    
    # utm_source
    st.sidebar.subheader("utm_source")
    utm_source = st.sidebar.text_input(
        "utm_source",
        value=st.session_state.utm_source,
        key="utm_source_input",
        placeholder="google, facebook, newsletter...",
        label_visibility="collapsed",
    )
    
    st.sidebar.divider()
    
    # utm_medium
    st.sidebar.subheader("utm_medium *")
    allow_empty_medium = st.sidebar.toggle(
        "Permitir vacío",
        value=st.session_state.allow_empty_medium,
        key="allow_empty_medium_toggle",
    )
    
    utm_medium_selected = st.sidebar.selectbox(
        "utm_medium",
        options=UTM_MEDIUM_OPTIONS,
        index=st.session_state.utm_medium_index,
        key="utm_medium_select",
        label_visibility="collapsed",
    )
    
    utm_medium_custom = ""
    if utm_medium_selected == "other":
        utm_medium_custom = st.sidebar.text_input(
            "Valor personalizado para utm_medium",
            value=st.session_state.utm_medium_custom,
            key="utm_medium_custom_input",
            placeholder="Escribe tu valor...",
        )
    
    st.sidebar.divider()
    
    # utm_campaign
    st.sidebar.subheader("utm_campaign *")
    allow_empty_campaign = st.sidebar.toggle(
        "Permitir vacío",
        value=st.session_state.allow_empty_campaign,
        key="allow_empty_campaign_toggle",
    )
    
    utm_campaign = st.sidebar.text_input(
        "utm_campaign",
        value=st.session_state.utm_campaign,
        key="utm_campaign_input",
        placeholder="verano2024, black_friday...",
        label_visibility="collapsed",
    )
    
    st.sidebar.divider()
    
    # utm_content
    st.sidebar.subheader("utm_content")
    utm_content = st.sidebar.text_input(
        "utm_content",
        value=st.session_state.utm_content,
        key="utm_content_input",
        placeholder="banner_hero, cta_footer...",
        label_visibility="collapsed",
    )
    
    st.sidebar.divider()
    
    # utm_testing
    st.sidebar.subheader("utm_testing")
    utm_testing = st.sidebar.text_input(
        "utm_testing",
        value=st.session_state.utm_testing,
        key="utm_testing_input",
        placeholder="test_a, variante_1...",
        label_visibility="collapsed",
    )
    
    st.sidebar.divider()
    
    # utm_product
    st.sidebar.subheader("utm_product")
    utm_product_selected = st.sidebar.selectbox(
        "utm_product",
        options=[""] + UTM_PRODUCT_OPTIONS,
        index=st.session_state.utm_product_index,
        key="utm_product_select",
        label_visibility="collapsed",
        format_func=lambda x: "Seleccionar..." if x == "" else x,
    )
    
    utm_product_otro = ""
    if utm_product_selected == "OTRO":
        utm_product_otro = st.sidebar.text_input(
            "Valor personalizado para utm_product",
            value=st.session_state.utm_product_otro,
            key="utm_product_otro_input",
            placeholder="Escribe tu producto...",
        )
    
    # Retornar todos los valores
    return {
        "url_base": url_base,
        "utm_source": utm_source,
        "utm_medium_selected": utm_medium_selected,
        "utm_medium_custom": utm_medium_custom,
        "allow_empty_medium": allow_empty_medium,
        "utm_campaign": utm_campaign,
        "allow_empty_campaign": allow_empty_campaign,
        "utm_content": utm_content,
        "utm_testing": utm_testing,
        "utm_product_selected": utm_product_selected,
        "utm_product_otro": utm_product_otro,
    }


def render_test_cases():
    """Renderiza la sección de casos de prueba."""
    with st.expander("🧪 Casos de prueba"):
        st.write("Haz clic en un botón para cargar el caso de prueba en el formulario:")
        
        cols = st.columns(2)
        
        for i, (case_name, case_data) in enumerate(TEST_CASES.items()):
            col = cols[i % 2]
            with col:
                if st.button(f"📋 {case_name}", key=f"test_case_{i}", use_container_width=True):
                    load_test_case(case_name)
                    st.rerun()
                
                st.caption(f"`{case_data['url']}`")


def main():
    """Función principal de la aplicación."""
    st.set_page_config(
        page_title="UTM Builder",
        page_icon="🔗",
        layout="wide",
    )
    
    init_session_state()
    
    # Título principal
    st.title("🔗 UTM Builder")
    st.markdown("Construye URLs con parámetros UTM de forma fácil y correcta.")
    
    # Renderizar sidebar y obtener valores
    inputs = render_sidebar()
    
    # Área principal
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("URL Final")
        
        # Validaciones
        errors = []
        warnings = []
        
        # Validar URL base
        url_valid, url_warning = validate_url(inputs["url_base"])
        if not url_valid:
            errors.append("La URL base es obligatoria.")
        elif url_warning:
            warnings.append(url_warning)
        
        # Validar utm_medium
        utm_medium_value = inputs["utm_medium_custom"] if inputs["utm_medium_selected"] == "other" else inputs["utm_medium_selected"]
        if not inputs["allow_empty_medium"] and not sanitize(utm_medium_value):
            errors.append("utm_medium es obligatorio. Activa 'Permitir vacío' si deseas omitirlo.")
        
        # Validar utm_campaign
        if not inputs["allow_empty_campaign"] and not sanitize(inputs["utm_campaign"]):
            errors.append("utm_campaign es obligatorio. Activa 'Permitir vacío' si deseas omitirlo.")
        
        # Mostrar errores
        for error in errors:
            st.error(error)
        
        # Mostrar warnings
        for warning in warnings:
            st.warning(warning)
        
        # Construir URL si no hay errores
        if not errors and inputs["url_base"]:
            # Procesar utm_medium
            utm_medium_final = utm_medium_value
            
            # Procesar utm_product
            utm_product_final = ""
            if inputs["utm_product_selected"] and inputs["utm_product_selected"] != "":
                utm_product_final = get_utm_product_value(
                    inputs["utm_product_selected"],
                    inputs["utm_product_otro"]
                )
            
            # Construir URL final
            final_url = build_final_url(
                base_url=inputs["url_base"],
                utm_source=inputs["utm_source"],
                utm_medium=utm_medium_final,
                utm_campaign=inputs["utm_campaign"],
                utm_content=inputs["utm_content"],
                utm_testing=inputs["utm_testing"],
                utm_product=utm_product_final,
            )
            
            # Mostrar URL final
            st.text_area(
                "URL con UTMs",
                value=final_url,
                height=100,
                key="final_url_output",
                label_visibility="collapsed",
            )
            
            # Botón para copiar
            st.code(final_url, language=None)
            st.caption("💡 Haz clic en el icono de copiar en la esquina superior derecha del bloque de código.")
            
            # Vista previa de parámetros
            st.subheader("Vista previa de parámetros")
            
            params = build_utm_params(
                utm_source=inputs["utm_source"],
                utm_medium=utm_medium_final,
                utm_campaign=inputs["utm_campaign"],
                utm_content=inputs["utm_content"],
                utm_testing=inputs["utm_testing"],
                utm_product=utm_product_final,
            )
            
            if params:
                param_df_data = {"Parámetro": [], "Valor": []}
                for name, value in params:
                    param_df_data["Parámetro"].append(name)
                    param_df_data["Valor"].append(value)
                
                st.table(param_df_data)
            else:
                st.info("No se han configurado parámetros UTM.")
        
        elif not errors:
            st.info("Ingresa una URL base para comenzar.")
    
    with col2:
        # Casos de prueba
        render_test_cases()
        
        # Información adicional
        with st.expander("ℹ️ Información"):
            st.markdown("""
            ### Campos obligatorios
            - **URL Base**: La URL a la que se agregarán los parámetros.
            - **utm_medium**: Requerido por defecto (activa el switch para omitir).
            - **utm_campaign**: Requerido por defecto (activa el switch para omitir).
            
            ### Orden de parámetros
            Los parámetros se agregan en este orden:
            1. utm_source
            2. utm_medium
            3. utm_campaign
            4. utm_content
            5. utm_testing
            6. utm_product
            
            ### Sanitización
            Los valores se sanitizan automáticamente:
            - Se eliminan espacios al inicio y final
            - Los espacios internos se reemplazan por `_`
            
            ### utm_product
            Los productos predefinidos se mapean a códigos estandarizados:
            - CUENTA DE AHORROS → CTA-AHORROS
            - CUENTA MAS → CTA-MAS
            - etc.
            """)


if __name__ == "__main__":
    main()
