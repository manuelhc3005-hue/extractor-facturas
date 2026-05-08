import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
import io
import base64
import os

# 1. Configuración de página
st.set_page_config(page_title="Reporte Especial | Extractor", page_icon="🧾", layout="wide")

# 2. Función para procesar la imagen de fondo
@st.cache_data
def obtener_base64_de_imagen(nombre_archivo):
    # Intentamos buscar el archivo con ambas extensiones por si acaso
    posibles_nombres = [nombre_archivo, "IMG_2284.jpg", "IMG_2284.jpeg"]
    for nombre in posibles_nombres:
        if os.path.exists(nombre):
            with open(nombre, "rb") as f:
                data = f.read()
            return base64.b64encode(data).decode()
    return ""

# Llamamos a la función
img_base64 = obtener_base64_de_imagen("IMG_2284.jpg")

# 3. Inyección de CSS (Fondo de foto + Transparencia)
if img_base64:
    st.markdown(f"""
        <style>
            [data-testid="stAppViewContainer"] {{
                background-image: url("data:image/jpeg;base64,{img_base64}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
            
            /* Ajuste de transparencia del contenedor para que se vea la foto */
            [data-testid="stAppViewContainer"] .main .block-container {{
                background-color: rgba(255, 255, 255, 0.88); 
                padding: 3rem;
                border-radius: 20px;
                margin-top: 3rem;
                box-shadow: 0 10px 30px rgba(0,0,0,0.4);
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
    st.error("No se pudo cargar la imagen de fondo. Verifica que 'IMG_2284.jpg' esté en la carpeta principal de GitHub.")

# 4. Encabezado de la página
st.markdown("<h1 class='main-title'>🧾 Reporte Especial de Facturación</h1>", unsafe_allow_html=True)
st.write("<p style='text-align: center; color: #4B5563;'>Esta sección cuenta con un motor de procesamiento optimizado y fondo personalizado.</p>", unsafe_allow_html=True)
st.divider()

# 5. Lógica de Procesamiento de XML
col1, col_centro, col2 = st.columns([1, 2, 1])

with col_centro:
    archivos_subidos = st.file_uploader("Arrastra aquí tus XML", type=["xml"], accept_multiple_files=True, key="uploader_especial")

if archivos_subidos:
    if st.button("⚙️ Procesar Facturas en modo Especial"):
        datos_facturas = []
        namespaces = {'cfdi': 'http://www.sat.gob.mx/cfd/4', 'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'}
        
        for archivo in archivos_subidos:
            try:
                tree = ET.parse(archivo)
                raiz = tree.getroot()
                
                # Extraer datos básicos (Compatibilidad 3.3 y 4.0)
                subtotal = raiz.get('SubTotal', '0')
                total = raiz.get('Total', '0')
                moneda = raiz.get('Moneda', 'MXN')
                
                # Emisor (usando búsqueda por tag para evitar problemas de namespace)
                emisor = raiz.find('.//{*}Emisor')
                rfc = emisor.get('Rfc', '') if emisor is not None else ''
                nombre = emisor.get('Nombre', '') if emisor is not None else ''
                
                # UUID
                timbre = raiz.find('.//{*}TimbreFiscalDigital')
                uuid = timbre.get('UUID', 'N/A') if timbre is not None else 'N/A'
                
                # Conceptos
                conceptos = raiz.findall('.//{*}Concepto')
                descripciones = [c.get('Descripcion', '') for c in conceptos]
                concepto_final = " / ".join(descripciones)
                
                # IVA (solo traslados)
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

            # Botón de descarga
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            
            st.download_button(
                label="📥 Descargar Reporte en Excel",
                data=buffer.getvalue(),
                file_name="Reporte_Especial.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
