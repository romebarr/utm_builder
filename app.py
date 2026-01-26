import streamlit as st
import re
from typing import List, Tuple, Optional

# -----------------------------------------------------------------------------
# Funciones Puras (Lógica de Negocio)
# -----------------------------------------------------------------------------

def sanitize(value: str) -> str:
    """
    Sanitiza el valor de entrada:
    - Elimina espacios al inicio y final (strip).
    - Reemplaza secuencias de espacios internos por un guion bajo (_).
    - Si el resultado es vacío, retorna cadena vacía.
    
    Args:
        value (str): Valor a sanitizar.
        
    Returns:
        str: Valor sanitizado.
    """
    if not value:
        return ""
    
    # Strip whitespace
    value = value.strip()
    
    # Reemplazar secuencias de espacios por _
    value = re.sub(r'\s+', '_', value)
    
    return value

def get_product_code(selection: str, custom_value: str) -> str:
    """
    Obtiene el código estandarizado para utm_product basado en la selección
    o el valor personalizado.
    
    Args:
        selection (str): Opción seleccionada del selectbox.
        custom_value (str): Valor ingresado si la selección fue 'OTRO'.
        
    Returns:
        str: Código estandarizado o valor sanitizado.
    """
    mapping = {
        "CUENTA DE AHORROS": "CTA-AHORROS",
        "CUENTA MAS": "CTA-MAS",
        "CUENTA MAXIMA": "CTA-MAXIMA",
        "BANKARD": "BANKARD",
        "CUENTA CORRIENTE": "CTA-CORRIENTE",
        "CREDIMAX": "CREDIMAX",
        "CUENTA NOMINA": "CTA-NOMINA",
        "PAGO DE SERVICIOS": "PAGO_SERVICIOS"
    }
    
    # Normalización para búsqueda en mapeo: trim, colapsar espacios, mayúsculas
    norm_selection = re.sub(r'\s+', ' ', selection.strip()).upper()
    
    if norm_selection in mapping:
        return mapping[norm_selection]
    
    # Si es OTRO o no está en el mapa, usar el valor custom
    # Nota: Si selection es "OTRO", usamos custom_value.
    # Si por alguna razón llega algo que no está en el mapa, asumimos fallback.
    
    if selection == "OTRO":
        return sanitize(custom_value)
        
    # Fallback por si acaso (ej. si pasaran un valor directo que no está en keys ni es OTRO)
    return sanitize(selection)

def append_query_params(url: str, params: List[Tuple[str, str]]) -> str:
    """
    Agrega parámetros de consulta a una URL base manejando los separadores ? y &.
    
    Args:
        url (str): URL base.
        params (list): Lista de tuplas (clave, valor) con los parámetros a agregar.
        
    Returns:
        str: URL final con parámetros concatenados.
    """
    if not params:
        return url
        
    url = url.strip()
    
    # Construir string de parámetros: key=value&key2=value2
    # Asumimos que params ya viene con valores sanitizados y filtrados (no vacíos)
    query_string = "&".join([f"{k}={v}" for k, v in params])
    
    if not query_string:
        return url
        
    # Lógica de separadores
    if url.endswith("?") or url.endswith("&"):
        return f"{url}{query_string}"
    
    if "?" in url:
        return f"{url}&{query_string}"
    
    return f"{url}?{query_string}"

# -----------------------------------------------------------------------------
# Interfaz de Usuario (Streamlit)
# -----------------------------------------------------------------------------

def main():
    st.set_page_config(page_title="UTM Builder", page_icon="🔗")
    st.title("UTM Builder")

    # --- Sidebar / Inputs ---
    with st.sidebar:
        st.header("Configuración")
        
        # 9) Casos de prueba internos
        with st.expander("Casos de prueba"):
            def load_test_case(url, source, medium, campaign):
                st.session_state.base_url_input = url
                st.session_state.utm_source_input = source
                st.session_state.utm_campaign_input = campaign
                
                # Logic for medium select/custom
                medium_options = [
                    "cpc", "paid_social", "email", "whatsapp", "push", "sms", 
                    "display", "referral", "organic", "affiliate", "social", "video", "other"
                ]
                
                if medium in medium_options:
                    st.session_state.utm_medium_select = medium
                    st.session_state.utm_medium_custom = ""
                else:
                    st.session_state.utm_medium_select = "other"
                    st.session_state.utm_medium_custom = medium

            if st.button("URL sin ?"):
                load_test_case("https://dominio.com/landing", "google", "cpc", "verano_2024")
                st.rerun()
                
            if st.button("URL con ?"):
                load_test_case("https://dominio.com/landing?ref=123", "facebook", "social", "promo_invierno")
                st.rerun()
                
            if st.button("URL terminando en ?"):
                load_test_case("https://dominio.com/landing?", "newsletter", "email", "boletin_semanal")
                st.rerun()
                
            if st.button("URL terminando en &"):
                load_test_case("https://dominio.com/landing?ref=123&", "linkedin", "referral", "b2b_leads")
                st.rerun()

    # Inputs principales
    # Usamos keys para vincular con session_state
    
    # Inicializar keys si no existen (para evitar KeyErrors en primer run si no se ha seteado)
    if "base_url_input" not in st.session_state: st.session_state.base_url_input = ""
    if "utm_source_input" not in st.session_state: st.session_state.utm_source_input = ""
    if "utm_campaign_input" not in st.session_state: st.session_state.utm_campaign_input = ""
    if "utm_medium_select" not in st.session_state: st.session_state.utm_medium_select = "cpc"
    if "utm_medium_custom" not in st.session_state: st.session_state.utm_medium_custom = ""
    
    base_url = st.text_input("URL base *", key="base_url_input")

    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        utm_source = st.text_input("utm_source", key="utm_source_input", help="Ej. google, facebook, newsletter")

        # UTM Campaign
        allow_empty_campaign = st.checkbox("Permitir utm_campaign vacío", value=False)
        label_campaign = "utm_campaign" + ("" if allow_empty_campaign else " *")
        utm_campaign = st.text_input(label_campaign, key="utm_campaign_input")
        
        utm_testing = st.text_input("utm_testing", help="Opcional")

    with col2:
        # UTM Medium
        allow_empty_medium = st.checkbox("Permitir utm_medium vacío", value=False)
        label_medium = "utm_medium" + ("" if allow_empty_medium else " *")
        
        medium_options = [
            "cpc", "paid_social", "email", "whatsapp", "push", "sms", 
            "display", "referral", "organic", "affiliate", "social", "video", "other"
        ]

        medium_selection = st.selectbox(label_medium, options=medium_options, key="utm_medium_select")
        
        utm_medium_final = ""
        if medium_selection == "other":
            utm_medium_custom = st.text_input("Especifique utm_medium", key="utm_medium_custom")
            utm_medium_final = utm_medium_custom
        else:
            utm_medium_final = medium_selection
        
        # UTM Content
        utm_content = st.text_input("utm_content", help="Opcional")
        
        # UTM Product
        product_options = [
            "CUENTA DE AHORROS", "CUENTA MAS", "CUENTA MAXIMA", "BANKARD", 
            "CUENTA CORRIENTE", "CREDIMAX", "CUENTA NOMINA", "PAGO DE SERVICIOS", "OTRO"
        ]
        product_selection = st.selectbox("utm_product", options=product_options)
        
        product_custom = ""
        if product_selection == "OTRO":
            product_custom = st.text_input("Especifique utm_product")

    # --- Procesamiento ---
    
    # 7) Validaciones
    errors = []
    
    if not base_url:
        st.info("Ingrese una URL base para comenzar.")
        return

    # Validar formato URL (warning)
    if not (base_url.startswith("http://") or base_url.startswith("https://")):
        st.warning("⚠️ La URL base no comienza con http:// o https://. Asegúrese de que sea correcta.")

    # Validar campos obligatorios
    if not allow_empty_medium and not sanitize(utm_medium_final):
        errors.append("utm_medium es obligatorio.")
    
    if not allow_empty_campaign and not sanitize(utm_campaign):
        errors.append("utm_campaign es obligatorio.")

    if errors:
        for err in errors:
            st.error(err)
        return

    # Preparar valores
    val_source = sanitize(utm_source)
    val_medium = sanitize(utm_medium_final)
    val_campaign = sanitize(utm_campaign)
    val_content = sanitize(utm_content)
    val_testing = sanitize(utm_testing)
    
    # Lógica especial producto
    val_product_raw = get_product_code(product_selection, product_custom)
    val_product = sanitize(val_product_raw) # Sanitize extra por si acaso

    # 5) Orden de parámetros
    # utm_source, utm_medium, utm_campaign, utm_content, utm_testing, utm_product
    params_list = []
    if val_source: params_list.append(("utm_source", val_source))
    if val_medium: params_list.append(("utm_medium", val_medium))
    if val_campaign: params_list.append(("utm_campaign", val_campaign))
    if val_content: params_list.append(("utm_content", val_content))
    if val_testing: params_list.append(("utm_testing", val_testing))
    if val_product: params_list.append(("utm_product", val_product))

    # Construir URL final
    final_url = append_query_params(base_url, params_list)

    # 6) Output
    st.markdown("### URL Final Generada")
    st.text_area("Copiar URL:", value=final_url, height=100)
    
    # Botón de copia (simulado con code block que tiene botón nativo en streamlit modernos, 
    # o simplemente instruyendo al usuario)
    st.caption("Copia la URL de arriba o usa el botón del bloque de código abajo:")
    st.code(final_url, language="text")

    st.markdown("### Vista previa de parámetros")
    if params_list:
        st.json(dict(params_list))
    else:
        st.write("No hay parámetros UTM para agregar.")

if __name__ == "__main__":
    main()
