# ============================================
# 🌱 APP DE NUTRICIÓN VEGETAL - MODULAR
# Autor: Carlos Maldonado + ChatGPT
# Versión: 1.0
# ============================================

import streamlit as st
import pandas as pd

# ============================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================
st.set_page_config(
    page_title="App de Nutrición Vegetal",
    page_icon="🌿",
    layout="wide",
)

st.title("🌿 Aplicación de Nutrición Vegetal")
st.markdown("**Versión inicial basada en cultivo de tomate — expandible a otros cultivos**")

# ============================================
# SECCIÓN 1 - Selección de cultivo
# ============================================
cultivo = st.selectbox(
    "Seleccione el cultivo:",
    ["Tomate", "Pepino (en desarrollo)", "Pimiento (en desarrollo)", "Fresa (en desarrollo)"]
)

# ============================================
# BASE DE DATOS DE ETAPAS (TOMATE)
# ============================================
if cultivo == "Tomate":
    etapas = {
        "A": {"dias": "0–14", "descripcion": "Establecimiento", "f": 0.25},
        "B": {"dias": "15–28", "descripcion": "Inicio crecimiento vegetativo", "f": 0.45},
        "C": {"dias": "29–42", "descripcion": "Vegetativo medio", "f": 0.65},
        "D": {"dias": "43–56", "descripcion": "Pre-floración / floración temprana", "f": 0.85},
        "E": {"dias": "57–70", "descripcion": "Pico de absorción (crítica)", "f": 1.00},
        "F": {"dias": "71–84", "descripcion": "Fructificación activa", "f": 0.95},
        "G": {"dias": "85–98", "descripcion": "Fructificación avanzada", "f": 0.70},
        "H": {"dias": "99–112+", "descripcion": "Maduración y fin de ciclo", "f": 0.45},
    }

    etapa_sel = st.selectbox("Seleccione la etapa fenológica:", list(etapas.keys()))
    f = etapas[etapa_sel]["f"]

    st.info(f"**Etapa {etapa_sel}** — {etapas[etapa_sel]['descripcion']} ({etapas[etapa_sel]['dias']} días) — Factor f = {f}")

    # Rangos base (etapa E)
    base = {
        "N": (160, 220),
        "P": (30, 60),
        "K": (200, 350),
        "Ca": (120, 200),
        "Mg": (30, 60),
        "S": (40, 80),
        "Fe": (1, 3),
        "Mn": (0.1, 0.5),
        "Zn": (0.02, 0.1)
    }

    # Calcular los valores ajustados por etapa
    rangos = {k: (v[0]*f, v[1]*f) for k, v in base.items()}
    df_rangos = pd.DataFrame(rangos).T
    df_rangos.columns = ["Mínimo (ppm)", "Máximo (ppm)"]

    st.subheader("Rangos recomendados por etapa (ppm)")
    st.dataframe(df_rangos.style.format("{:.2f}"))

# ============================================
# SECCIÓN 2 - Datos de la solución de suelo
# ============================================
st.subheader("🧪 Ingrese los valores de su solución nutritiva (ppm)")
cols = st.columns(3)
N = cols[0].number_input("Nitrógeno (N)", 0.0)
P = cols[1].number_input("Fósforo (P)", 0.0)
K = cols[2].number_input("Potasio (K)", 0.0)
Ca = cols[0].number_input("Calcio (Ca)", 0.0)
Mg = cols[1].number_input("Magnesio (Mg)", 0.0)
S = cols[2].number_input("Azufre (S)", 0.0)

Fe = cols[0].number_input("Hierro (Fe)", 0.0)
Mn = cols[1].number_input("Manganeso (Mn)", 0.0)
Zn = cols[2].number_input("Zinc (Zn)", 0.0)

# ============================================
# SECCIÓN 3 - Fertilizantes disponibles
# ============================================
st.subheader("🧴 Marque los fertilizantes que tiene disponibles")
fertilizantes = [
    "Nitrato de calcio",
    "Nitrato de potasio",
    "Sulfato de magnesio",
    "Fosfato monoamónico (MAP)",
    "Sulfato de potasio",
    "Urea",
    "Quelato de hierro",
    "Quelato de zinc",
    "Quelato de manganeso"
]
disp = st.multiselect("Seleccione los fertilizantes disponibles:", fertilizantes)

# ============================================
# SECCIÓN 4 - Datos de riego
# ============================================
st.subheader("💧 Datos del sistema de riego")

longitud_cama = st.number_input("Longitud de cada cama (metros):", min_value=1.0, step=0.1)
num_camas = st.number_input("Número de camas:", min_value=1, step=1)
dist_goteros = st.number_input("Distancia entre goteros (cm):", min_value=1.0, step=1.0)
caudal_gotero = st.number_input("Caudal por gotero (L/h):", min_value=0.1, step=0.1)
horas_riego = st.number_input("Tiempo de riego (horas):", min_value=0.1, step=0.1)

# Calcular volumen total

goteros_por_cama = (longitud_cama * 100) / dist_goteros
volumen_total = goteros_por_cama * caudal_gotero * num_camas * horas_riego

st.success(f"💧 Volumen total aplicado: **{volumen_total:.2f} L**")

# ============================================
# SECCIÓN 5 - Cálculo de déficit / exceso
# ============================================
if cultivo == "Tomate" and volumen_total > 0:
    st.subheader("📊 Resultados del análisis")

    data_usuario = {"N": N, "P": P, "K": K, "Ca": Ca, "Mg": Mg, "S": S, "Fe": Fe, "Mn": Mn, "Zn": Zn}
    resultados = []

    for elemento, valor in data_usuario.items():
        min_val, max_val = rangos[elemento]
        if valor < min_val:
            estado = "Déficit"
            diff = min_val - valor
        elif valor > max_val:
            estado = "Exceso ⚠️"
            diff = valor - max_val
        else:
            estado = "Óptimo ✅"
            diff = 0
        resultados.append([elemento, valor, min_val, max_val, estado, diff])

    df_result = pd.DataFrame(resultados, columns=["Elemento", "Actual (ppm)", "Mínimo", "Máximo", "Estado", "Diferencia"])

    # Columnas que deberían ser numéricas
    numeric_cols = ["Actual (ppm)", "Mínimo", "Máximo", "Diferencia"]

    # Convertir a float de manera segura
    for col in numeric_cols:
        df_result[col] = pd.to_numeric(df_result[col], errors='coerce')  # valores no convertibles -> NaN

    # Función para formatear solo números
    def format_numeric(x):
        if pd.isna(x):
            return ""  # o "N/A" si prefieres
        else:
            return f"{x:.2f}"

    # Aplicar formato solo a columnas numéricas
    st.dataframe(df_result.style.format({col: format_numeric for col in numeric_cols}))

    # ============================================
    # ADVERTENCIAS POR EXCESOS Y ANTAGONISMOS
    # ============================================
    st.subheader("⚠️ Advertencias y observaciones")
    advertencias = []

    if N > rangos["N"][1]:
        advertencias.append("Exceso de N puede reducir absorción de Ca y K.")
    if K > rangos["K"][1]:
        advertencias.append("Exceso de K puede antagonizar la absorción de Mg y Ca.")
    if Ca > rangos["Ca"][1]:
        advertencias.append("Exceso de Ca puede reducir absorción de Mg y K.")
    if Mg > rangos["Mg"][1]:
        advertencias.append("Exceso de Mg puede afectar disponibilidad de Ca.")
    if Fe > rangos["Fe"][1]:
        advertencias.append("Exceso de Fe puede precipitar con fosfatos.")

    if advertencias:
        for a in advertencias:
            st.warning(a)
    else:
        st.success("No se detectaron excesos ni antagonismos importantes.")

    # ============================================
    # RECOMENDACIÓN DE FERTILIZACIÓN BALANCEADA
    # ============================================
    st.subheader("🧮 Plan de nutrición balanceado (solo déficit)")

    # Diccionario con % de nutrientes en fertilizantes disponibles
    contenido_fert = {
        "Urea": {"N": 46},
        "Nitrato de calcio": {"N": 15.5, "Ca": 19},
        "Nitrato de potasio": {"N": 13, "K": 46},
        "Sulfato de magnesio": {"Mg": 9.8, "S": 13},
        "Fosfato monoamónico (MAP)": {"P": 52, "N": 11},
        "Sulfato de potasio": {"K": 50, "S": 18},
        "Quelato de hierro": {"Fe": 6},
        "Quelato de manganeso": {"Mn": 12},
        "Quelato de zinc": {"Zn": 14}
    }

    # Inicializar déficits en ppm
    deficits = {}
    for elem, valor in data_usuario.items():
        min_val, max_val = rangos[elem]
        deficits[elem] = max(min_val - valor, 0)  # 0 si no hay déficit

    plan = []

    # Iterar sobre nutrientes con déficit
    for elem, deficit_ppm in deficits.items():
        if deficit_ppm <= 0:
            continue  # no necesita fertilizante

        # Buscar un fertilizante disponible que contenga el nutriente
        fert_usado = None
        kg_fert = None
        gramos_nutriente = None
        for fert in disp:
            if elem in contenido_fert.get(fert, {}):
                porcentaje = contenido_fert[fert][elem] / 100

                # Calcular gramos de nutriente a añadir
                gramos_nutriente = (deficit_ppm * volumen_total) / 1000  # g

                # Calcular kg de fertilizante
                kg_fert = gramos_nutriente / (porcentaje * 1000)  # g → kg
                fert_usado = fert

                # Ajustar déficits de otros nutrientes que aporta este fertilizante
                for otro_elem, pct in contenido_fert[fert].items():
                    if otro_elem == elem:
                        continue
                    aporte_ppm = (kg_fert * 1000 * pct / 100) / volumen_total  # g → ppm
                    deficits[otro_elem] = max(deficits.get(otro_elem, 0) - aporte_ppm, 0)

                break  # usamos solo un fertilizante por nutriente

        plan.append([
            elem,
            round(deficit_ppm, 2),
            fert_usado,
            round(gramos_nutriente, 2) if gramos_nutriente else None,
            round(kg_fert, 3) if kg_fert else None,
            round(deficits.get(elem, 0), 2)
        ])

    # Crear DataFrame final
    df_plan = pd.DataFrame(plan, columns=[
        "Elemento", "Déficit inicial (ppm)", "Fertilizante recomendado", 
        "Gramos nutriente", "Kg fertilizante", "Déficit restante (ppm)"
    ])

    # Formatear columnas numéricas
    numeric_cols = ["Déficit inicial (ppm)", "Gramos nutriente", "Kg fertilizante", "Déficit restante (ppm)"]
    def format_numeric(x):
        if pd.isna(x):
            return ""
        else:
            return f"{x:.2f}"

    # Mostrar tabla en Streamlit
    st.dataframe(df_plan.style.format({col: format_numeric for col in numeric_cols}))

    # FERTILIZANTES DISPONIBLES
    st.subheader("🔍 Revisión de disponibilidad de fertilizantes")
    fert_recom = {
        "N": "Nitrato de calcio, nitrato de potasio o Urea",
        "P": "MAP o MKP",
        "K": "Nitrato de potasio o sulfato de potasio",
        "Ca": "Nitrato de calcio",
        "Mg": "Sulfato de magnesio",
        "Fe": "Quelato de hierro",
        "Mn": "Quelato de manganeso",
        "Zn": "Quelato de zinc"
    }

    for elem, fert in fert_recom.items():
        if elem in df_plan["Elemento"].values:
            if not any(f in disp for f in fert.split(" o ")):
                st.error(f"Falta un fertilizante adecuado para **{elem}** → Recomendado: {fert}")
            else:
                st.success(f"Tienes fertilizantes adecuados para **{elem}** ✅")

# ============================================
# FIN DE LA APP
# ============================================
st.markdown("---")
st.caption("Desarrollado por Carlos Maldonado")

