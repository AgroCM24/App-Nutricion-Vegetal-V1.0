# streamlit_nutricion.py
import streamlit as st
import pandas as pd
import traceback

st.set_page_config(page_title="Nutrición Vegetal (integrada)", layout="centered")

# ------------------------
# Datos base (tomate) - rangos por etapa (ppm)
# ------------------------
rangos_etapas = {
    'A': {'DDT': (0,14), 'f': 0.25, 'N': (40,55), 'P': (7,17), 'K': (45,97), 'Ca': (30,55),
          'Mg': (7,17), 'S': (9,22), 'Fe': (0.22,0.83), 'Mn': (0.03,0.14), 'Zn': (0.006,0.028)},
    'B': {'DDT': (15,28), 'f': 0.45, 'N': (65,110), 'P': (12,30), 'K': (90,174), 'Ca': (60,99),
          'Mg': (15,30), 'S': (18,40), 'Fe': (0.40,1.48), 'Mn': (0.05,0.25), 'Zn': (0.01,0.05)},
    'C': {'DDT': (29,42), 'f': 0.65, 'N': (93,143), 'P': (18,39), 'K': (130,228), 'Ca': (78,143),
          'Mg': (17,43), 'S': (26,57), 'Fe': (0.58,2.15), 'Mn': (0.07,0.36), 'Zn': (0.015,0.065)},
    'D': {'DDT': (43,56), 'f': 0.85, 'N': (122,187), 'P': (22,46), 'K': (153,328), 'Ca': (102,187),
          'Mg': (20,52), 'S': (34,75), 'Fe': (0.76,2.83), 'Mn': (0.09,0.46), 'Zn': (0.02,0.08)}
}

# ------------------------
# Sales: fracción (g_nutriente / g_sal)
# Nota: valores simplificados. Ajustar si tienes datos exactos.
# ------------------------
sales = {
    'Ca(NO3)2·4H2O': {'Ca': 0.2, 'N': 0.15},
    'KNO3': {'K': 0.2, 'N': 0.13},
    'KH2PO4': {'K': 0.12, 'P': 0.22},
    'MgSO4': {'Mg': 0.10, 'S': 0.15}
}

interpretacion_ref = {
    'deficit': 'Deficiencia — considerar aporte progresivo de la sal recomendada.',
    'exceso': 'Exceso — ajustar la salinidad y diluir con agua de riego.'
}

# ------------------------
# Funciones principales (tratan de emular la lógica del notebook original)
# ------------------------
def evaluar_mediciones(info_etapa, mediciones):
    resultados = []
    for nutr, med in mediciones.items():
        if nutr in info_etapa:
            rmin, rmax = info_etapa[nutr]
            if med < rmin:
                estado = 'Deficiencia'
            elif med > rmax:
                estado = 'Exceso'
            else:
                estado = 'OK'
            resultados.append({
                'Nutriente': nutr,
                'Medición (ppm)': med,
                'Rango objetivo (ppm)': f"{rmin}-{rmax}",
                'Estado': estado
            })
    return pd.DataFrame(resultados)

def calcular_deficit_mg_per_L(row):
    # row has Medición and Rango objetivo like "min-max"
    try:
        rmin = float(row['Rango objetivo (ppm)'].split('-')[0])
        med = float(row['Medición (ppm)'])
        return max(0.0, rmin - med)
    except Exception:
        return 0.0

def sugerir_mezcla_greedy(deficits_mg_L_dict, sales_map, volumen_tanque_L, info_etapa):
    """
    Algoritmo greedy simplificado:
    - Para cada nutriente deficitario, prueba las sales que contienen ese nutriente.
    - Calcula gramos necesarios por L y por tanque.
    - Simula el efecto sobre otros nutrientes y evita propuestas que produzcan excedentes (si es posible).
    - Si no hay opción sin excedente, devuelve la mejor opción ignorando parcialmente la restricción.
    """
    propuestas = []
    # Comenzamos con un vector de aporte 0 para todos los nutrientes
    aportes_ppm = {nutr: 0.0 for nutr in ['N','P','K','Ca','Mg','S','Fe','Mn','Zn']}
    for nutr, deficit_mg_L in deficits_mg_L_dict.items():
        if deficit_mg_L <= 0:
            continue
        opciones = []
        for sal, comps in sales_map.items():
            if nutr not in comps or comps[nutr] <= 0:
                continue
            factor = comps[nutr]  # g_nutriente por g_sal
            gramos_sal_por_L = (deficit_mg_L / 1000.0) / factor  # g_sal per L
            gramos_para_tanque = gramos_sal_por_L * volumen_tanque_L
            # Simular aporte que agregaría por L a otros nutrientes
            sim_aportes = {}
            produce_exceso = False
            for otro, frac in comps.items():
                aumento_ppm = frac * gramos_sal_por_L * 1000.0  # g_sal/L * frac (g_nutr/g_sal) -> g_nutr/L -> *1000 mg/g -> mg/L -> ppm
                sim_aportes[otro] = aumento_ppm
                # comparar con max aceptable (rango max del objetivo)
                if otro in info_etapa:
                    _, rmax = info_etapa[otro]
                    # si el aporte potencial + actual excede bastante el max, marcar
                    # Nota: no tenemos "actual" interno aquí, solo asumimos que se podría exceder; 
                    # esta comprobación será más precisa cuando se combine con mediciones reales.
                    # Para seguridad usamos un umbral (ej. 5% del rmax)
                    if aumento_ppm > (0.5 * rmax):  # regla conservadora: si una sola sal aporta >50% del máximo, advertir
                        produce_exceso = True
            opciones.append({'sal': sal, 'g_per_L': gramos_sal_por_L, 'g_tanque': gramos_para_tanque, 'sim_aportes': sim_aportes, 'produce_exceso': produce_exceso})
        # Priorizar opciones que NO produzcan exceso y orden por gramos para tanque
        opciones_aceptables = [o for o in opciones if not o['produce_exceso']]
        if opciones_aceptables:
            opciones_sel = sorted(opciones_aceptables, key=lambda x: x['g_tanque'])
        else:
            opciones_sel = sorted(opciones, key=lambda x: x['g_tanque'])
        # tomar top 2 opciones para mostrar
        for o in opciones_sel[:2]:
            propuestas.append({
                'Nutriente': nutr,
                'Sal propuesta': o['sal'],
                'g_por_L (sal)': round(o['g_per_L'], 6),
                'g_para_tanque': round(o['g_tanque'], 3),
                'Advertencia_exceso': o['produce_exceso']
            })
    return pd.DataFrame(propuestas)

# ------------------------
# INTERFAZ STREAMLIT
# ------------------------
try:
    st.title("🌿 Nutrición Vegetal — Integración completa")
    st.markdown("Esta versión intenta integrar la lógica de evaluación y mezcla. Si se produce un error, verás el detalle abajo.")

    # Sidebar
    st.sidebar.header("Configuración")
    cultivos = ['Tomate', 'Lechuga (en desarrollo)', 'Fresa (en desarrollo)', 'Pepino (en desarrollo)']
    cultivo = st.sidebar.selectbox("Selecciona cultivo:", cultivos)
    volumen_tanque = st.sidebar.number_input("Volumen tanque (L)", value=200.0, min_value=1.0, step=1.0)

    st.sidebar.markdown("---")
    st.sidebar.markdown("Cálculo por riego (opcional)")
    caudal_cinta_L_h = st.sidebar.number_input("Caudal por cinta (L/h)", value=1.0, min_value=0.0, step=0.1)
    num_cintas = st.sidebar.number_input("Número de cintas", value=10, min_value=1, step=1)
    horas_riego = st.sidebar.number_input("Horas de riego por ciclo", value=1.0, min_value=0.0, step=0.1)

    if cultivo != "Tomate":
        st.warning("Datos completos disponibles solo para Tomate. Otros cultivos en desarrollo.")

    # Tabla de etapas (DDT)
    st.subheader("Etapas y rango de días (DDT)")
    etapas_rows = [{'Etapa': e, 'Días (DDT desde-hasta)': f"{v['DDT'][0]} - {v['DDT'][1]} días"} for e, v in rangos_etapas.items()]
    st.table(pd.DataFrame(etapas_rows))

    # Selección de etapa
    st.subheader("Selecciona etapa")
    etapa_opcion = st.selectbox("Etapa", ['A', 'B', 'C', 'D'])
    info_etapa = rangos_etapas[etapa_opcion]

    # Mostrar rangos por nutriente
    st.markdown(f"### Rangos objetivo — Tomate (Etapa {etapa_opcion})")
    nut_rows = []
    for nutr, val in info_etapa.items():
        if nutr in ['DDT', 'f']:
            continue
        nut_rows.append({'Nutriente': nutr, 'Min (ppm)': val[0], 'Max (ppm)': val[1]})
    st.dataframe(pd.DataFrame(nut_rows), use_container_width=True)

    # Inputs: mediciones actuales
    st.subheader("Ingresa tus mediciones actuales (ppm)")
    col1, col2, col3 = st.columns(3)
    with col1:
        N_med = st.number_input("N (ppm)", value=100.0, step=1.0)
        P_med = st.number_input("P (ppm)", value=20.0, step=1.0)
    with col2:
        K_med = st.number_input("K (ppm)", value=150.0, step=1.0)
        Ca_med = st.number_input("Ca (ppm)", value=80.0, step=1.0)
    with col3:
        Mg_med = st.number_input("Mg (ppm)", value=25.0, step=1.0)
        S_med = st.number_input("S (ppm)", value=30.0, step=1.0)

    mediciones = {'N': N_med, 'P': P_med, 'K': K_med, 'Ca': Ca_med, 'Mg': Mg_med, 'S': S_med}

    if st.button("✅ Evaluar y sugerir mezcla"):
        st.info(f"Evaluando mediciones para Tomate — Etapa {etapa_opcion}")
        resultados_df = evaluar_mediciones(info_etapa, mediciones)
        # calcular deficits mg/L (ppm)
        resultados_df['Deficit_mg_L'] = resultados_df.apply(calcular_deficit_mg_per_L, axis=1)
        st.table(resultados_df)

        # construir dict de deficits por nutriente
        deficits = {}
        for _, r in resultados_df.iterrows():
            if r['Estado'] == 'Deficiencia':
                deficits[r['Nutriente']] = r['Deficit_mg_L']

        if deficits:
            st.error("Deficiencias detectadas: " + ", ".join(deficits.keys()))
            # Sugerir mezcla (algoritmo simplificado)
            sugerencias_df = sugerir_mezcla_greedy(deficits, sales, volumen_tanque, info_etapa)
            if not sugerencias_df.empty:
                st.markdown("#### Sugerencias de sales y cantidades (estimadas)")
                st.dataframe(sugerencias_df, use_container_width=True)
                st.download_button("Descargar sugerencias CSV", sugerencias_df.to_csv(index=False).encode('utf-8'),
                                   file_name="sugerencias_sales.csv")
            else:
                st.info("No se encontraron sales adecuadas en la base simplificada.")
        else:
            st.success("No se detectaron déficits en los nutrientes evaluados.")

    st.markdown("---")
    st.subheader("Cálculo rápido: gramos por tanque y por riego")
    sal_sel = st.selectbox("Selecciona sal (ejemplos)", list(sales.keys()))
    dosis_mg_L = st.number_input("Dosis objetivo (mg/L) (nutriente que quieres aportar)", value=100.0, step=1.0)

    if st.button("Calcular gramos para tanque y por riego"):
        comps = sales.get(sal_sel, {})
        if not comps:
            st.error("Sal seleccionada no encontrada")
        else:
            # select nutrient with highest fraction for messaging
            nutr_target = max(comps.items(), key=lambda x: x[1])[0]
            factor = comps[nutr_target]
            if factor <= 0:
                st.error("Factor de sal inválido")
            else:
                gramos_por_L = (dosis_mg_L / 1000.0) / factor
                gramos_para_tanque = gramos_por_L * volumen_tanque
                litros_por_riego = caudal_cinta_L_h * num_cintas * horas_riego
                gramos_por_riego = gramos_por_L * litros_por_riego
                st.success(f"Usando {sal_sel} (aporta especialmente {nutr_target}):")
                st.write(f"- Gramos por litro (sal): {gramos_por_L:.4f} g/L")
                st.write(f"- Gramos para {volumen_tanque:.0f} L tanque: {gramos_para_tanque:.2f} g")
                st.write(f"- Litros por ciclo de riego: {litros_por_riego:.1f} L")
                st.write(f"- Gramos por ciclo de riego: {gramos_por_riego:.2f} g")

    st.caption("Notas: conversiones estimadas. Para replicar con exactitud la mezcla avanzada del notebook, puedo añadir la función original punto por punto.")
except Exception as e:
    st.error("Se produjo una excepción al iniciar la app. Copia el error y pásamelo para ayudar a depurar:")
    st.code(traceback.format_exc())
