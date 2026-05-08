import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
import io

# Configuración de la página
st.set_page_config(page_title="Extractor de Facturas CFDI", page_icon="📊", layout="centered")

st.title("📊 Extractor de Facturas XML (CFDI)")
st.write("Sube tus facturas en formato XML para extraer los datos y descargar un reporte limpio en Excel.")

# 1. Cargador de archivos web
archivos_subidos = st.file_uploader("Arrastra aquí tus archivos XML", type=["xml"], accept_multiple_files=True)

if archivos_subidos:
    if st.button("Procesar Facturas"):
        datos_facturas = []
        namespaces = {
            'cfdi4': 'http://www.sat.gob.mx/cfd/4',
            'cfdi3': 'http://www.sat.gob.mx/cfd/3',
            'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'
        }

        # Barra de progreso visual
        barra_progreso = st.progress(0)
        
        for i, archivo in enumerate(archivos_subidos):
            try:
                tree = ET.parse(archivo)
                raiz = tree.getroot()
                
                # Detectar versión CFDI
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
            
            # Actualizar barra de progreso
            barra_progreso.progress((i + 1) / len(archivos_subidos))

        # 2. Crear DataFrame y mostrar vista previa
        if datos_facturas:
            cols = ["FACTURA", "RFC", "NOMBRE DEL PROVEEDOR", "CONCEPTO", "SUBTOTAL", "IMPORTE IVA", "IMPORTE TOTAL EN PESOS", "Moneda"]
            df = pd.DataFrame(datos_facturas, columns=cols)
            
            st.success(f"¡Se procesaron {len(datos_facturas)} facturas con éxito!")
            st.write("Vista previa de los datos:")
            st.dataframe(df) # Muestra una tablita en la web

            # 3. Preparar el Excel para descargar en memoria
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Facturas')
            
            # 4. Botón de descarga web
            st.download_button(
                label="📥 Descargar Reporte en Excel",
                data=buffer.getvalue(),
                file_name="Reporte_Gastos_XML.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )