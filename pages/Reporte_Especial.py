import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
import io
import base64
import os

# 1. Configuración de página
st.set_page_config(page_title="Reporte Especial | Extractor", page_icon="🧾", layout="wide")

# 2. Función para leer la imagen (ajustada para encontrarla seguro)
@st.cache_data
def obtener_base64_de_imagen():
    ruta_script = os.path.dirname(__file__) 
    # Subimos un nivel para encontrar la imagen en la raíz del proyecto
    ruta_imagen = os.path.join(ruta_script, "..", "IMG_2284.jpeg")
    
    try:
        if os.path.exists(ruta_imagen):
            with open(ruta_imagen, "rb") as f:
                data = f.read()
            return base64.b64encode(data).decode()
        return None
    except Exception:
        return None

img_base_64 = obtener_base64_de_imagen()

# 3. Inyección de CSS de "Alta Prioridad"
if img_base_64:
    st.markdown(
        f"""
        <style>
        /* Targeteamos el contenedor principal de la App */
        [data-testid="stAppViewContainer"] {{
            background-image: url("data:image/jpeg;base64,{img_base_64}") !important;
            background-size: cover !important;
            background-position: center !important;
            background-repeat: no-repeat !important;
            background-attachment: fixed !important;
        }}

        /* Hacemos que la parte central sea transparente para ver el fondo */
        [data-testid="stHeader"], .main, .stApp {{
            background: rgba(0,0,0,0) !important;
            background-color: rgba(0,0,0,0) !important;
        }}

        /* Creamos una caja blanca semi-transparente para el contenido */
        .block-container {{
            background-color: rgba(255, 255, 255, 0.92) !important;
            padding: 3rem !important;
            border-radius: 20px !important;
            margin-top: 50px !important;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5) !important;
        }}
        
        /* Ajuste de color de textos para que se lean sobre el blanco */
        h1, h2, h3, p, span, label {{
            color: #1f3a93 !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
else:
    st.error("🚨 Error: No se pudo cargar 'IMG_2284.jpeg'. Revisa que el nombre en GitHub sea exacto.")

# 4. Título y lógica funcional
st.markdown("<h1 style='text-align: center;'>🧾 Procesador Especial</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Sube tus archivos XML y disfruta del fondo personalizado.</p>", unsafe_allow_html=True)
st.divider()

# Contenedor de carga de archivos
archivos = st.file_uploader("Selecciona tus archivos XML", type=["xml"], accept_multiple_files=True)

if archivos:
    if st.button("🚀 Procesar Facturas Ahora"):
        datos = []
        barra = st.progress(0)
        
        for i, arch in enumerate(archivos):
            try:
                tree = ET.parse(arch)
                root = tree.getroot()
                
                # Extracción de datos (UUID, RFC y Total)
                uuid = "N/A"
                timbre = root.find('.//{*}TimbreFiscalDigital')
                if timbre is not None: uuid = timbre.get('UUID')
                
                emisor = root.find('.//{*}Emisor')
                rfc = emisor.get('Rfc', 'N/A')
                nombre = emisor.get('Nombre', 'N/A')
                total = root.get('Total', '0')
                
                datos.append({
                    "FACTURA": uuid,
                    "RFC": rfc,
                    "PROVEEDOR": nombre,
                    "TOTAL": float(total)
                })
            except:
                st.error(f"Error con el archivo: {arch.name}")
            
            barra.progress((i + 1) / len(archivos))
        
        if datos:
            df = pd.DataFrame(datos)
            st.success("¡Procesamiento completo!")
            st.dataframe(df, use_container_width=True)
            
            # Generar Excel
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            
            st.download_button(
                label="📥 Descargar Reporte Excel",
                data=buffer.getvalue(),
                file_name="Reporte_Especial_Broma.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
