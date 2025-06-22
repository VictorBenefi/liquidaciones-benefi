import streamlit as st

# Lista de usuarios y contraseñas permitidos (podés editar o ampliar)
USUARIOS_AUTORIZADOS = {
    "admin": "clave123",
    "victor": "benefi2024",
    # Agregá más usuarios si querés
}

# Inicializar sesión
if "logueado" not in st.session_state:
    st.session_state.logueado = False

# Si no está logueado, mostrar formulario
if not st.session_state.logueado:
    st.title("🔒 Ingreso a BENEFI")

    usuario = st.text_input("Usuario")
    clave = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):
        if usuario in USUARIOS_AUTORIZADOS and USUARIOS_AUTORIZADOS[usuario] == clave:
            st.session_state.logueado = True
            st.experimental_rerun()
        else:
            st.error("Usuario o contraseña incorrectos")

# Si está logueado, mostrar el resto de la app
if st.session_state.logueado:
    st.success(f"Bienvenido {usuario} 👋")
    # 🔽 Acá abajo empieza tu app como siempre


import streamlit as st
import pandas as pd
from io import BytesIO
from openpyxl import load_workbook
from openpyxl.styles import Font, Alignment
from datetime import datetime

st.title("💰 Sistema de Liquidaciones con IVA - Benefi")

# Subida del archivo
archivo = st.file_uploader("📁 Subí el archivo Excel", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)

    columnas_necesarias = {"red", "Total_Ventas", "Cantidad_Ventas", "Costo_Amin", "Costo_Tr"}

    if columnas_necesarias.issubset(df.columns):
        # Cálculos
        df["Costo_Admin"] = df["Total_Ventas"] * df["Costo_Amin"]
        df["Costo_Transaccion"] = df["Cantidad_Ventas"] * df["Costo_Tr"]
        df["Subtotal"] = df["Costo_Admin"] + df["Costo_Transaccion"]
        df["IVA_21%"] = df["Subtotal"] * 0.21
        df["Total_Cobrar"] = df["Subtotal"] + df["IVA_21%"]

        st.subheader("📊 Resultado de la liquidación")
        st.dataframe(df)

        # Fecha actual
        hoy = datetime.today()
        nombre_mes = hoy.strftime('%B').capitalize()
        fecha_str = hoy.strftime('%d de %B de %Y').capitalize()

        # Guardar Excel con formato y encabezado
        salida = BytesIO()
        with pd.ExcelWriter(salida, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Liquidación", startrow=3)
            hoja = writer.sheets["Liquidación"]

            # Encabezado principal
            hoja.merge_cells("A1:F1")
            celda1 = hoja["A1"]
            celda1.value = "BENEFI - LIQUIDACIÓN MENSUAL"
            celda1.font = Font(size=14, bold=True)
            celda1.alignment = Alignment(horizontal="center")

            # Subencabezado con mes y fecha
            hoja.merge_cells("A2:F2")
            celda2 = hoja["A2"]
            celda2.value = f"Corresponde a {nombre_mes.upper()} {hoy.year} - Generado el {fecha_str}"
            celda2.font = Font(size=11, italic=True)
            celda2.alignment = Alignment(horizontal="center")

            # Formato moneda
            columnas_monedas = ["Costo_Admin", "Costo_Transaccion", "Subtotal", "IVA_21%", "Total_Cobrar"]
            for col in hoja.iter_cols(min_row=4, max_row=hoja.max_row):
                if col[0].value in columnas_monedas:
                    for celda in col[1:]:
                        celda.number_format = '"$"#,##0.00'

        st.download_button(
            label="📥 Descargar Excel con encabezado y formato",
            data=salida.getvalue(),
            file_name="Cobrar_liquidacion_junio.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    else:
        st.error("❗ El archivo debe tener las columnas: red, Total_Ventas, Cantidad_Ventas, Costo_Amin, Costo_Tr")
