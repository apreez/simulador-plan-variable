import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Carga Masiva", layout="wide")

st.title("📂 Carga Masiva - Plan Variable")

st.sidebar.header("⚙️ Configuración del Plan")

target = st.sidebar.number_input("Target mensual ($)", value=614400)

meta_isn = st.sidebar.number_input("Meta ISN", value=85)
meta_clientes = st.sidebar.number_input("Meta Clientes Efectivos", value=200)
meta_prod = st.sidebar.number_input("Meta Productividad", value=12)
meta_sb = st.sidebar.number_input("Meta Tasa SB", value=10)

peso_isn = 0.20
peso_clientes = 0.30
peso_prod = 0.25
peso_sb = 0.25

def calcular_factor(cumplimiento):
    if cumplimiento < 80:
        return 0
    elif cumplimiento < 90:
        return 0.8
    elif cumplimiento < 100:
        return 1.0
    elif cumplimiento < 110:
        return 1.1
    else:
        return 1.2

def calcular_kpi(resultado, meta, peso, tipo="mayor"):
    if tipo == "mayor":
        cumplimiento = (resultado / meta) * 100
    else:
        cumplimiento = (meta / resultado) * 100 if resultado != 0 else 0

    cumplimiento = min(cumplimiento, 125)

    factor = calcular_factor(cumplimiento)
    aporte = peso * factor

    return cumplimiento, aporte

uploaded_file = st.file_uploader("Subir archivo Excel", type=["xlsx"])

if uploaded_file:

    df = pd.read_excel(uploaded_file, engine="openpyxl")

    resultados = []

    for _, row in df.iterrows():

        c1, a1 = calcular_kpi(row["ISN"], meta_isn, peso_isn)
        c2, a2 = calcular_kpi(row["CLIENTES EFECTIVOS"], meta_clientes, peso_clientes)
        c3, a3 = calcular_kpi(row["PRODUCTIVIDAD"], meta_prod, peso_prod)
        c4, a4 = calcular_kpi(row["TASA SOLICITUD DE BAJA"], meta_sb, peso_sb, "menor")

        total_factor = a1 + a2 + a3 + a4
        total = target * total_factor

        cumplimiento_total = min((total / target) * 100, 125)

        resultados.append({
            "Nombre": row["Nombre"],
            "ISN": row["ISN"],
            "CLIENTES EFECTIVOS": row["CLIENTES EFECTIVOS"],
            "TASA SOLICITUD DE BAJA": row["TASA SOLICITUD DE BAJA"],
            "PRODUCTIVIDAD": row["PRODUCTIVIDAD"],
            "CUMPLIMIENTO": round(cumplimiento_total,2),
            "MONTO $": round(total,0)
        })

    df_resultado = pd.DataFrame(resultados)

    st.dataframe(df_resultado)

    output = BytesIO()
    df_resultado.to_excel(output, index=False)
    output.seek(0)

    st.download_button(
        label="📥 Descargar Resultados Excel",
        data=output,
        file_name="resultado_variable.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
