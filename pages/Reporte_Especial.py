import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
import io

# 1. Configuración de página
st.set_page_config(page_title="Xx_Reporte_Especial_xX", page_icon="💀", layout="wide")

# 2. CSS Estilo Emo / Hi5 / MySpace (Puro Código)
st.markdown("""
    <style>
        /* Fondo Negro Profundo */
        .stApp {
            background-color: #000000 !important;
            color: #FF007F !important;
        }

        /* Contenedor Principal con borde rosa punteado (muy Hi5) */
        .block-container {
            background-color: #0a0a0a !important;
            border: 3px dashed #FF007F !important;
            padding: 2rem !important;
            border-radius: 0px !important;
            margin-top: 2rem !important;
        }

        /* Títulos Estilo "Gótico/Emo" */
        h1 {
            color: #FF007F !important;
            text-shadow: 2px 2px #5D00FF, 4px 4px #000000;
            font-family: 'Courier New', Courier, monospace;
            text-align: center;
            text-transform: uppercase;
            letter-spacing: 5px;
        }

        /* Subtítulos y textos */
        .emo-text {
            color: #FFFFFF !important;
            text-align: center;
            font-family: 'Tahoma', sans-serif;
            font-size: 0.9rem;
        }

        /* Botones Rosa Neón con Hover Negro */
        div.stButton > button:first-child {
            background-color: #FF007F !important;
            color: white !important;
            border: 2px solid #FFFFFF !important;
            border-radius: 0px !important;
            font-weight: bold;
            width: 100%;
            transition: 0.3s;
        }
        div.stButton > button:first-child:hover {
            background-color: #000000 !important;
            color: #FF007F !important;
            border: 2px solid #FF007F !important;
        }

        /* Estilo del Dataframe (Tabla) */
        [data-testid="stDataFrame"] {
            border: 1px solid #FF007F !important;
        }

        /* Input de archivos */
        [data-testid="stFileUploader"] {
            background-color: #1a1a1a !important;
            border: 1px solid #5D00FF !important;
            color: #FF007F !important;
        }

        /* Animación de Estrellas/Glitter simple */
        @keyframes sparkle {
            0% { opacity: 0.2; }
            50% { opacity: 1; }
            100% { opacity: 0.2; }
        }
        .glitter {
            color: #FFFFFF;
            animation: sparkle 1s infinite;
        }
    </style>
""", unsafe_allow_html=True)

# 3. Encabezado "Retro"
st.markdown("<h1>† Reporte Especial †</h1>", unsafe_allow_html=True)
st.markdown("<p class='emo-text'><span class='glitter'>★</span> Mood: Incomprendido <span class='glitter'>★</span></p>", unsafe_allow_html=True)
st.markdown("<p class='emo-text'>&copy; 2007 Manu_Broken_Heart - No acepto F/F si no firmas mi libro</p>", unsafe_allow_html=True)
st.divider()

# 4. Lógica Funcional
col1, col_centro, col2 = st.columns([1, 2, 1])

with col_centro:
    archivos_subidos = st.file_uploader("SubE TuS ArCHiVoS XML aQuI...", type=["xml"], accept_multiple_files=True)

if archivos_subidos:
    st.write("<br>", unsafe_allow_html=True)
    if st.button("X_PROCESAR_FACTURAS_X"):
        datos_facturas = []
        for archivo in archivos_subidos:
            try:
                tree = ET.parse(archivo)
                raiz = tree.getroot()
                total = raiz.get('Total', '0')
                emisor = raiz.find('.//{*}Emisor')
                nombre = emisor.get('Nombre', 'Desconocido')
                datos_facturas.append({"PROVEEDOR": nombre, "TOTAL": float(total)})
            except:
                st.error(f"Err0r en: {archivo.name}")

        if datos_facturas:
            df = pd.DataFrame(datos_facturas)
            st.success("¡¡ToDo SuBIdO CoN ExITo!!")
            
            # Tabla con estilo
            st.markdown("<p style='color:#FF007F;'>MiS DaToS:</p>", unsafe_allow_html=True)
            st.dataframe(df, use_container_width=True)

            # Botón de Descarga
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            
            st.download_button(
                label="📥 dEsCaRgAr ExCeL",
                data=buffer.getvalue(),
                file_name="Reporte_Emo.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

# 5. Footer "Hi5 Style"
st.divider()
st.markdown("<p style='text-align:center; font-size: 10px; color: #555;'>Diseño por: Xx_Manu_Engineer_xX | 2007-2026 | mCr rOcKs</p>", unsafe_allow_html=True)
