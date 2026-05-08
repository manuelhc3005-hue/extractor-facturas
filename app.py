import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
import io

# 1. Configuración de página (Layout ancho y título)
st.set_page_config(page_title="Extractor CFDI | Finanzas", page_icon="🧾", layout="wide")

# 2. Inyección de CSS personalizado para mejorar el diseño
st.markdown("""
    <style>
        /* Título principal */
        .main-title {
            text-align: center;
            color: #1E3A8A;
            font-family: 'Helvetica Neue', sans-serif;
            font-weight: 700;
        }
        /* Subtítulo */
        .sub-title {
            text-align: center;
            color: #6B7280;
            font-size: 1.1rem;
            margin-bottom: 2rem;
        }
        /* Botón de Procesar (Azul) */
        div.stButton > button:first-child {
            background-color: #2563EB;
            color: white;
            border-radius: 8px;
            padding: 10px 24px;
            font-weight: bold;
            border: none;
            width: 100%;
        }
        div.stButton > button:first-child:hover {
            background-color: #1D4ED8;
            color: white;
        }
        /* Botón de Descarga (Verde) */
        div.stDownloadButton > button:first-child {
            background-color: #10B981;
            color: white;
            border-radius: 8px;
            padding: 10px 24px;
            font-weight: bold;
            border: none;
        }
        div.stDownloadButton > button:first-child:hover {
            background-color: #059669;
            color: white;
        }
        /* Tarjetas de métricas */
        div[data-testid="stMetricValue"] {
            font-size: 2rem;
            color: #1E3A8A;
        }
    </style>
""", unsafe_allow_html=True)

# 3. Encabezado Visual
st.markdown("<h1 class='main-title'>🧾 Extractor Inteligente de Facturas CFDI</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Sube tus archivos XML y genera un reporte contable estructurado en segundos.</p>", unsafe_allow_html=True)
st.divider()

# 4. Zona de carga (centrada usando columnas)
col_espacio1, col_centro, col_espacio2 = st.columns([1, 2, 1])

with col_centro:
    st.info("💡 **Tip:** Puedes arrastrar múltiples archivos XML al mismo tiempo.")
    archivos_subidos = st.file_uploader("", type=["xml"], accept_multiple_files=True)

if archivos_subidos:
    st.write("<br>", unsafe_allow_html=True) # Espacio extra
    
    # Botón centrado
    _, col_btn, _ = st.columns([1, 1, 1])
    with col_btn:
        procesar = st.button("⚙️ Procesar Facturas")

    if procesar:
        datos_facturas = []
        namespaces = {
            'cfdi4': 'http://www.sat.gob.mx/cfd/4',
            'cfdi3': 'http://www.sat.gob.mx/cfd/3',
            'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'
        }

        # Barra de progreso visual
        barra_progreso = st.progress(0)
        st.write("Analizando nodos XML...")
        
        for i, archivo in enumerate(archivos_subidos):
            try:
                tree = ET.parse(archivo)
                raiz = tree.getroot()
                
                ns = 'cfdi4' if 'cfdv40.xsd' in raiz.attrib.get('{http://www.w3.org/2001/XMLSchema-instance}schemaLocation', '') else 'cfdi3'
                
                subtotal = float(raiz.get('SubTotal', 0.0))
                total = float(raiz.get('Total', 0.0))
                moneda = raiz.get('Moneda', 'MXN')
                
                emisor = raiz.find(f'{ns}:Emisor', namespaces)
                rfc = emisor.get('Rfc', '') if emisor is not None else ''
                nombre = emisor.get('Nombre', '') if emisor is not None else ''
                
                complemento = raiz.find(f'{ns}:Complemento', namespaces)
                timbre = complemento.find('tfd:TimbreFiscalDigital', namespaces) if complemento is not None else None
                uuid = timbre.get('UUID', '') if timbre is not None else 'N/A'
                
                conceptos_nodo = raiz.find(f'{ns}:Conceptos', namespaces)
                if conceptos_nodo is not None:
                    descripciones = [c.get('Descripcion', '') for c in conceptos_nodo.findall(f'{ns}:Concepto', namespaces)]
                    concepto_final = " / ".join(descripciones)
                else:
                    concepto_final = ""
                
                iva_importe = 0.0
                impuestos_globales = raiz.find(f'{ns}:Impuestos', namespaces)
                if impuestos_globales is not None:
                    traslados = impuestos_globales.find(f'{ns}:Traslados', namespaces)
                    if traslados is not None:
                        for t in traslados.findall(f'{ns}:Traslado', namespaces):
                            if t.get('Impuesto') == '002':
                                iva_importe += float(t.get('Importe', 0.0))
                
                datos_facturas.append([uuid, rfc, nombre, concepto_final, subtotal, iva_importe, total, moneda])
            
            except Exception as e:
                st.error(f"Error al leer el archivo {archivo.name}: {e}")
            
            # Actualizar barra
            barra_progreso.progress((i + 1) / len(archivos_subidos))

        # 5. Resultados y Dashboard
        if datos_facturas:
            cols = ["FACTURA", "RFC", "NOMBRE DEL PROVEEDOR", "CONCEPTO", "SUBTOTAL", "IMPORTE IVA", "IMPORTE TOTAL EN PESOS", "Moneda"]
            df = pd.DataFrame(datos_facturas, columns=cols)
            
            # Limpiar barra y mostrar éxito
            barra_progreso.empty()
            st.success("¡Análisis completado con éxito!")
            
            # --- TARJETAS DE MÉTRICAS (DASHBOARD) ---
            st.markdown("### 📊 Resumen de Gastos")
            metrica1, metrica2, metrica3 = st.columns(3)
            
            total_facturas = len(df)
            suma_total = df['IMPORTE TOTAL EN PESOS'].sum()
            
            metrica1.metric("Facturas Procesadas", f"{total_facturas} archivos")
            metrica2.metric("Suma Total (MXN)", f"${suma_total:,.2f}")
            metrica3.metric("Estado", "100% OK")
            
            st.divider()

            # Tabla de previsualización
            st.markdown("### 📋 Vista Previa de Datos")
            st.dataframe(df, use_container_width=True)

            # 6. Preparar Excel y Botón
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Facturas')
            
            st.write("<br>", unsafe_allow_html=True)
            col_descarga1, col_descarga2, col_descarga3 = st.columns([1, 2, 1])
            with col_descarga2:
                st.download_button(
                    label="📥 Descargar Reporte Final en Excel",
                    data=buffer.getvalue(),
                    file_name="Reporte_Gastos_XML.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
