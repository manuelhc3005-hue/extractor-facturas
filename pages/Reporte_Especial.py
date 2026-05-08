import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
import io
import base64

# 1. Configuración de página
st.set_page_config(page_title="Reporte Especial | Extractor", page_icon="🧾", layout="wide")

# 2. Función para procesar la imagen de fondo
@st.cache_data
def obtener_base64_de_imagen(ruta_archivo):
    try:
        with open(ruta_archivo, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception as e:
        return ""

# Cargamos la foto que ya subiste a GitHub
img_base64 = obtener_base64_de_imagen("IMG_2284.jpeg")

# 3. Inyección de CSS (Fondo de foto + Transparencia para leer datos)
st.markdown(f"""
    <style>
        /* Foto de fondo */
        [data-testid="stAppViewContainer"] {{
            background-image: url("data:image/jpeg;base64,{img_base64}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        
        /* Capa para que el contenido sea legible sobre la foto */
        [data-testid="stAppViewContainer"] .main .block-container {{
            background-color: rgba(255, 255, 255, 0.90); 
            padding: 2rem 3rem;
            border-radius: 15px;
            margin-top: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        }}

        .main-title {{
            text-align: center;
            color: #1E3A8A;
            font-family: 'Helvetica Neue', sans-serif;
        }}

        /* Estilo de botones */
        div.stButton > button:first-child {{
            background-color: #2563EB;
            color: white;
            width: 100%;
        }}
        div.stDownloadButton > button:first-child {{
            background-color: #10B981;
            color: white;
            width: 100%;
        }}
    </style>
""", unsafe_allow_html=True)

# 4. Encabezado de la página
st.markdown("<h1 class='main-title'>🧾 Reporte Especial de Facturación</h1>", unsafe_allow_html=True)
st.write("Esta sección cuenta con un motor de procesamiento optimizado (y un fondo de pantalla personalizado).")
st.divider()

# 5. Lógica de Procesamiento de XML
col_espacio1, col_centro, col_espacio2 = st.columns([1, 2, 1])

with col_centro:
    st.markdown("### 📁 Cargar Facturas")
    archivos_subidos = st.file_uploader("", type=["xml"], accept_multiple_files=True, key="uploader_especial")

if archivos_subidos:
    st.write("<br>", unsafe_allow_html=True)
    _, col_btn, _ = st.columns([1, 1, 1])
    
    with col_btn:
        procesar = st.button("⚙️ Procesar Facturas")

    if procesar:
        datos_facturas = []
        namespaces = {
            'cfdi4': 'http://www.sat.gob.mx/cfd/4',
            'cfdi3': 'http://www.sat.gob.mx/cfdi/3',
            'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'
        }

        barra_progreso = st.progress(0)
        
        for i, archivo in enumerate(archivos_subidos):
            try:
                tree = ET.parse(archivo)
                raiz = tree.getroot()
                
                ns = 'cfdi4' if 'cfdv40.xsd' in raiz.attrib.get('{http://www.w3.org/2001/XMLSchema-instance}schemaLocation', '') else 'cfdi3'
                
                subtotal = float(raiz.get('SubTotal', 0.0))
                total = float(raiz.get('Total', 0.0))
                moneda = raiz.get('Moneda', 'MXN')
                
                emisor = raiz.find(f'{{{namespaces[ns]}}}Emisor') or raiz.find(f'cfdi:Emisor', namespaces)
                rfc = emisor.get('Rfc', '') if emisor is not None else ''
                nombre = emisor.get('Nombre', '') if emisor is not None else ''
                
                complemento = raiz.find(f'{{{namespaces[ns]}}}Complemento') or raiz.find(f'cfdi:Complemento', namespaces)
                timbre = complemento.find('tfd:TimbreFiscalDigital', namespaces) if complemento is not None else None
                uuid = timbre.get('UUID', '') if timbre is not None else 'N/A'
                
                conceptos_nodo = raiz.find(f'{{{namespaces[ns]}}}Conceptos') or raiz.find(f'cfdi:Conceptos', namespaces)
                if conceptos_nodo is not None:
                    descripciones = [c.get('Descripcion', '') for c in conceptos_nodo.findall(f'{{{namespaces[ns]}}}Concepto') or conceptos_nodo.findall(f'cfdi:Concepto', namespaces)]
                    concepto_final = " / ".join(descripciones)
                else:
                    concepto_final = ""
                
                iva_importe = 0.0
                impuestos_nodo = raiz.find(f'{{{namespaces[ns]}}}Impuestos') or raiz.find(f'cfdi:Impuestos', namespaces)
                if impuestos_nodo is not None:
                    traslados = impuestos_nodo.find(f'{{{namespaces[ns]}}}Traslados') or impuestos_nodo.find(f'cfdi:Traslados', namespaces)
                    if traslados is not None:
                        for t in traslados.findall(f'{{{namespaces[ns]}}}Traslado') or traslados.findall(f'cfdi:Traslado', namespaces):
                            if t.get('Impuesto') == '002':
                                iva_importe += float(t.get('Importe', 0.0))
                
                datos_facturas.append([uuid, rfc, nombre, concepto_final, subtotal, iva_importe, total, moneda])
            
            except Exception as e:
                st.error(f"Error en {archivo.name}: {e}")
            
            barra_progreso.progress((i + 1) / len(archivos_subidos))

        if datos_facturas:
            cols = ["FACTURA", "RFC", "NOMBRE DEL PROVEEDOR", "CONCEPTO", "SUBTOTAL", "IMPORTE IVA", "IMPORTE TOTAL EN PESOS", "Moneda"]
            df = pd.DataFrame(datos_facturas, columns=cols)
            
            barra_progreso.empty()
            st.success(f"¡{len(datos_facturas)} facturas procesadas con éxito!")
            
            # Dashboard de resumen
            metrica1, metrica2 = st.columns(2)
            metrica1.metric("Total Facturas", len(df))
            metrica2.metric("Suma Total (MXN)", f"${df['IMPORTE TOTAL EN PESOS'].sum():,.2f}")
            
            st.dataframe(df, use_container_width=True)

            # Botón de Descarga
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            
            st.download_button(
                label="📥 Descargar Reporte Especial (Excel)",
                data=buffer.getvalue(),
                file_name="Reporte_Broma_Exitoso.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
