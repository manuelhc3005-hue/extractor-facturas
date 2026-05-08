import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
import io
import base64
import os

# 1. Configuración de página
st.set_page_config(page_title="Reporte Especial | Extractor", page_icon="🧾", layout="wide")

# 2. Función para leer la imagen
@st.cache_data
def obtener_base64_de_imagen():
    ruta_script = os.path.dirname(__file__) 
    # Asegúrate que el nombre sea exactamente IMG_2284.jpeg (o .jpg según tu GitHub)
    ruta_imagen = os.path.join(ruta_script, "..", "IMG_2284.jpeg")
    
    try:
        with open(ruta_imagen, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception:
        return None

img_base_64 = obtener_base64_de_imagen()

# 3. Inyección de estilo (Aquí es donde forzamos la vista)
if img_base_64:
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url("data:image/jpeg;base64,{img_base_64}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        /* Hacemos que el contenedor de los archivos sea legible pero deje ver el fondo */
        .block-container {{
            background-color: rgba(255, 255, 255, 0.9);
            padding: 2.5rem !important;
            border-radius: 15px;
            margin-top: 50px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }}
        
        /* Quitamos fondos grises de Streamlit */
        header, .stHeader {{
            background-color: rgba(0,0,0,0) !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
else:
    st.warning("No se pudo cargar la imagen de fondo. Verifica el nombre del archivo en GitHub.")

# 4. Título y lógica
st.markdown("<h2 style='text-align: center; color: #1f3a93;'>🧾 Procesador de Reportes Especiales</h2>", unsafe_allow_html=True)

# Contenedor de carga
archivos = st.file_uploader("Sube tus archivos XML aquí", type=["xml"], accept_multiple_files=True)

if archivos:
    if st.button("Procesar Facturas"):
        datos = []
        for arch in archivos:
            try:
                tree = ET.parse(arch)
                root = tree.getroot()
                
                # Extracción simple de datos
                total = root.get('Total', '0')
                rfc_emisor = root.find('.//{*}Emisor').get('Rfc', 'N/A')
                nombre_emisor = root.find('.//{*}Emisor').get('Nombre', 'N/A')
                
                datos.append({"RFC": rfc_emisor, "Nombre": nombre_emisor, "Total": float(total)})
            except Exception as e:
                st.error(f"Error en {arch.name}")
        
        if datos:
            df = pd.DataFrame(datos)
            st.success(f"¡{len(datos)} facturas procesadas!")
            st.dataframe(df, use_container_width=True)
            
            # Botón de descarga
            towrite = io.BytesIO()
            df.to_excel(towrite, index=False, engine='openpyxl')
            st.download_button(label="Descargar Excel", data=towrite.getvalue(), file_name="reporte.xlsx")
