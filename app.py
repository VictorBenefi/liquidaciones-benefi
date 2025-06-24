import streamlit as st
import pandas as pd
from pathlib import Path
from io import BytesIO
from datetime import datetime

st.title("🧪 Validador de archivo de liquidación")

archivo = st.file_uploader("📥 Subí tu archivo Excel", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)

    # Mostrar columnas detectadas
    st.write("Columnas detectadas:", df.columns.tolist())

    columnas_necesarias = {"red", "Total_Ventas", "Cantidad_Ventas", "Costo_Amin", "Costo_Tr"}

    if columnas_necesarias.issubset(df.columns):
        st.success("✅ El archivo es válido")

        df["Costo_Admin"] = df["Total_Ventas"] * df["Costo_Amin"]
        df["Costo_Transaccion"] = df["Cantidad_Ventas"] * df["Costo_Tr"]
        df["Subtotal"] = df["Costo_Admin"] + df["Costo_Transaccion"]
        df["IVA_21%"] = df["Subtotal"] * 0.21
        df["Total_Cobrar"] = df["Subtotal"] + df["IVA_21%"]

        st.dataframe(df)

        Path("historial").mkdir(exist_ok=True)
        fecha = datetime.now().strftime("%Y-%m-%d")
        nombre_archivo = f"historial/liquidacion_test_{fecha}.xlsx"

        # Guardar archivo
        salida = BytesIO()
        df.to_excel(salida, index=False)

        with open(nombre_archivo, "wb") as f:
            f.write(salida.getvalue())

        st.download_button(
            "⬇️ Descargar archivo generado",
            data=salida.getvalue(),
            file_name=nombre_archivo.split("/")[-1],
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.error("❌ El archivo no tiene las columnas necesarias")
