import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# CONFIGURACIÓN DE PÁGINA
# -----------------------------
st.set_page_config(page_title="Simulador Variable", layout="wide")

st.title("📊 Simulador Gerencial - Plan Variable")

# -----------------------------
# SIDEBAR CONFIGURACIÓN PLAN
# -----------------------------
st.sidebar.header("⚙️ Configuración del Plan")

target = st.sidebar.number_input("Target mensual ($)", value=768000)

max_errores = st.sidebar.number_input("Máx. errores críticos", value=3)

cap_max = st.sidebar.number_input("Cap máximo ($) (0 = sin cap)", value=0)

if cap_max == 0:
    cap_max = None

st.sidebar.subheader("🎯 Metas del Mes")

meta_isn = st.sidebar.number_input("Meta ISN", value=85)
meta_clientes = st.sidebar.number_input("Meta Clientes Efectivos", value=100)
meta_prod = st.sidebar.number_input("Meta Productividad", value=12)
meta_sb = st.sidebar.number_input("Meta Tasa SB", value=5)

st.sidebar.subheader("⚖️ Ponderaciones (%)")

peso_isn = st.sidebar.slider("ISN", 0, 100, 20) / 100
peso_clientes = st.sidebar.slider("Clientes", 0, 100, 30) / 100
peso_prod = st.sidebar.slider("Productividad", 0, 100, 25) / 100
peso_sb = st.sidebar.slider("Tasa SB", 0, 100, 25) / 100

if round(peso_isn + peso_clientes + peso_prod + peso_sb, 2) != 1.0:
    st.sidebar.error("⚠️ Las ponderaciones deben sumar 100%")

# -----------------------------
# FUNCIÓN CÁLCULO SIMPLE
# -----------------------------
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

    factor = calcular_factor(cumplimiento)
    aporte = peso * factor

    return cumplimiento, factor, aporte

# -----------------------------
# INPUT RESULTADOS
# -----------------------------
st.header("📈 Simulación de Resultados")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    r_isn = st.number_input("ISN Real", value=90)

with col2:
    r_clientes = st.number_input("Clientes Efectivos", value=110)

with col3:
    r_prod = st.number_input("Productividad", value=13)

with col4:
    r_sb = st.number_input("Tasa SB", value=4)

with col5:
    errores = st.number_input("Errores Críticos", value=2)

# -----------------------------
# CÁLCULO
# -----------------------------
if st.button("🚀 Calcular"):

    # 🔴 Si supera errores críticos → penalización 50%
    if errores > max_errores:

        st.warning("⚠️ Supera errores críticos: KPIs penalizados al 50%")

        # Cada KPI aporta su peso * 0.5
        aporte_isn = peso_isn * 0.5
        aporte_clientes = peso_clientes * 0.5
        aporte_prod = peso_prod * 0.5
        aporte_sb = peso_sb * 0.5

        total_factor = aporte_isn + aporte_clientes + aporte_prod + aporte_sb
        total = target * total_factor

        if cap_max:
            total = min(total, cap_max)

        st.markdown("## 💰 Resultado Final")
        st.success(f"${total:,.0f}")

        df = pd.DataFrame({
            "KPI": ["ISN", "Clientes", "Productividad", "Tasa SB"],
            "Cumplimiento %": ["Penalizado", "Penalizado", "Penalizado", "Penalizado"],
            "Factor": [0.5, 0.5, 0.5, 0.5]
        })

    else:

        # 🟢 Cálculo normal
        c1 = calcular_kpi(r_isn, meta_isn, peso_isn, "mayor")
        c2 = calcular_kpi(r_clientes, meta_clientes, peso_clientes, "mayor")
        c3 = calcular_kpi(r_prod, meta_prod, peso_prod, "mayor")
        c4 = calcular_kpi(r_sb, meta_sb, peso_sb, "menor")

        total_factor = c1[2] + c2[2] + c3[2] + c4[2]
        total = target * total_factor

        if cap_max:
            total = min(total, cap_max)

        st.markdown("## 💰 Resultado Final")
        st.success(f"${total:,.0f}")

        df = pd.DataFrame({
            "KPI": ["ISN", "Clientes", "Productividad", "Tasa SB"],
            "Cumplimiento %": [c1[0], c2[0], c3[0], c4[0]],
            "Factor": [c1[1], c2[1], c3[1], c4[1]]
        })

    st.dataframe(df)

    # Gráfico
    if errores > max_errores:
        df_plot = pd.DataFrame({
            "KPI": ["ISN", "Clientes", "Productividad", "Tasa SB"],
            "Aporte": [aporte_isn, aporte_clientes, aporte_prod, aporte_sb]
        })
    else:
        df_plot = pd.DataFrame({
            "KPI": ["ISN", "Clientes", "Productividad", "Tasa SB"],
            "Aporte": [c1[2], c2[2], c3[2], c4[2]]
        })

    fig = px.bar(df_plot, x="KPI", y="Aporte", title="Impacto por KPI")
    st.plotly_chart(fig, use_container_width=True)