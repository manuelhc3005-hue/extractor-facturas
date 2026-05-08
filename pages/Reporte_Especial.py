import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
import io
import base64
import os

# 1. Configuración de página
st.set_page_config(page_title="Reporte Especial | Extractor", page_icon="🧾", layout="wide")

# 2. Función para leer la imagen y asegurar que el código sea limpio
@st.cache_data
def obtener_base64_de_imagen():
    ruta_script = os.path.dirname(__file__) 
    ruta_imagen = os.path.join(ruta_script, "..", "IMG_2284.jpeg")
    
    try:
        with open(ruta_imagen, "rb") as f:
            data = f.read()
        # El replace quita cualquier salto de línea que pueda romper el navegador
        return base64.b64encode(data).decode().replace('\n', '')
    except Exception as e:
        return None

img_base64 = obtener_base64_de_imagen()

# 3. El Hack HTML/CSS Definitivo
if img_base64:
    st.markdown(f"""
        <img src="data:image/jpeg;base64,{img_base64}" 
             style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; object-fit: cover; z-index: -999;">
        
        <style>
            /* Volvemos invisibles las capas grises de Streamlit */
            .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
                background: transparent !important;
                background-color: transparent !important;
            }}
            
            /* Diseñamos la caja blanca central para que resalte sobre la foto */
            .block-container {{
                background-color: rgba(255, 255, 255, 0.95) !important; 
                padding: 3rem !important;
                border-radius: 20px !important;
                box-shadow: 0 10px 40px rgba(0,0,0,0.6) !important;
                margin-top: 2rem !important;
            }}

            .main-title {{
                text-align: center;
                color: #1E3A8A;
                font-family: 'Helvetica Neue', sans-serif;
                font-weight: 800;
            }}
        </style>
    """, unsafe_allow_html=True)
else:
    st.error("🚨 No se encontró la imagen IMG_2284.jpeg")

# 4. Encabezado de la página
st.markdown("<h1 class='main-title'>🧾 Reporte Especial de Facturación</h1>", unsafe_allow_html=True)
st.write("<p style='text-align: center; color: #4B5563; font-weight: bold;'>Esta sección cuenta con un motor de procesamiento optimizado y fondo personalizado.</p>", unsafe_allow_html=True)
st.divider()

# 5. Lógica de Procesamiento de XML
col1, col_centro, col2 = st.columns([1, 2, 1])

with col_centro:
    archivos_subidos = st.file_uploader(
        label="Carga tus XML", 
        type=["xml"], 
        accept_multiple_files=True, 
        key="uploader_especial",
        label_visibility="collapsed"
    )

if archivos_subidos:
    st.write("<br>", unsafe_allow_html=True)
    _, col_btn, _ = st.columns([1, 1, 1])
    
    with col_btn:
        if st.button("⚙️ Procesar Facturas Especiales", use_container_width=True):
            datos_facturas = []
            
            for archivo in archivos_subidos:
                try:
                    tree = ET.parse(archivo)
                    raiz = tree.getroot()
                    
                    subtotal = raiz.get('SubTotal', '0')
                    total = raiz.get('Total', '0')
                    moneda = raiz.get('Moneda', 'MXN')
                    
                    emisor = raiz.find('.//{*}Emisor')
                    rfc = emisor.get('Rfc', '') if emisor is not None else ''
                    nombre = emisor.get('Nombre', '') if emisor is not None else ''
                    
                    timbre = raiz.find('.//{*}TimbreFiscalDigital')
                    uuid = timbre.get('UUID', 'N/A') if timbre is not None else 'N/A'
                    
                    conceptos = raiz.findall('.//{*}Concepto')
                    descripciones = [c.get('Descripcion', '') for c in conceptos]
                    concepto_final = " / ".join(descripciones)
                    
                    iva_total = 0.0
                    impuestos = raiz.findall('.//{*}Traslado')
                    for imp in impuestos:
                        if imp.get('Impuesto') == '002':
                            iva_total += float(imp.get('Importe', 0))
                    
                    datos_facturas.append([uuid, rfc, nombre, concepto_final, float(subtotal), iva_total, float(total), moneda])
                except Exception as e:
                    st.error(f"Error en {archivo.name}: {e}")

            if datos_facturas:
                cols = ["FACTURA", "RFC", "NOMBRE DEL PROVEEDOR", "CONCEPTO", "SUBTOTAL", "IMPORTE IVA", "IMPORTE TOTAL", "Moneda"]
                df = pd.DataFrame(datos_facturas, columns=cols)
                
                st.success("¡Procesado terminado!")
                st.dataframe(df, use_container_width=True)

                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False)
                
                st.download_button(
                    label="📥 Descargar Reporte Especial",
                    data=buffer.getvalue(),
                    file_name="Reporte_Broma.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
