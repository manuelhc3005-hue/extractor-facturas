import streamlit as st
import base64

st.set_page_config(page_title="Reporte Confidencial", page_icon="🔒", layout="wide")

# Función para leer la imagen que subimos y convertirla en código automáticamente
@st.cache_data
def obtener_base64_de_imagen(ruta_archivo):
    try:
        with open(ruta_archivo, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception as e:
        return ""

# Llamamos a la foto que acabas de subir a GitHub (asegúrate de que el nombre sea exacto)
img_base64 = obtener_base64_de_imagen("IMG_2284.jpeg")

# Inyectamos el CSS con la imagen
st.markdown(f"""
    <style>
        [data-testid="stAppViewContainer"] {{
            background-image: url("data:image/jpeg;base64,{img_base64}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        [data-testid="stHeader"] {{
            background-color: rgba(0,0,0,0);
        }}
        .caja-broma {{
            background-color: rgba(255, 255, 255, 0.85);
            padding: 2rem;
            border-radius: 12px;
            text-align: center;
            margin-top: 2rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
    </style>
""", unsafe_allow_html=True)

# El texto de la broma
st.markdown("""
    <div class="caja-broma">
        <h1 style="color: #1E3A8A;">🚨 ¡ERROR EN EL SISTEMA FINANCIERO! 🚨</h1>
        <h3 style="color: #6B7280;">Se han detectado movimientos no reconocidos en la cuenta...</h3>
        <p>Por favor, revisa el fondo de pantalla para identificar al sospechoso.</p>
    </div>
""", unsafe_allow_html=True)

if st.button("Contactar a Soporte Técnico"):
    st.error("Soporte Técnico se está riendo en este momento. Intenta más tarde.")
