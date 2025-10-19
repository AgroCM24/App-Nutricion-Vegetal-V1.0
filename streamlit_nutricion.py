# ============================================
# 🌱 APP DE NUTRICIÓN VEGETAL - FINAL PROTOTIPO
# Autor: Carlos Maldonado + ChatGPT
# Versión: 2.3
# ============================================

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# Para Google Sheets
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ============================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================
st.set_page_config(
    page_title="App de Nutrición Vegetal",
    page_icon="🌿",
    layout="wide",
)

st.title("🌿 Aplicación de Nutrición Vegetal")
st.markdown("**Versión 2.3 - Modular con IA y guardado en Google Sheets**")

# ============================================
# MENÚ PRINCIPAL
# ============================================
opcion_menu = st.sidebar.radio(
    "Seleccione la sección:",
    ["Interpretación clásica", "Interpretación con IA"]
)

# ============================================
# SELECCIÓN DE CULTIVO
# ============================================
if opcion_menu == "Interpretación clásica":
    cultivo_clasico = st.selectbox(
        "Seleccione el cultivo:",
        ["Tomate", "Pepino", "Pimiento", "Fresa"],
        key="cultivo_clasico"
    )
# ============================================
# CONFIGURACIÓN GOOGLE SHEETS
# ============================================
try:
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credenciales.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("Nutricion_Vegetal").sheet1
except Exception as e:
    st.warning("No se pudo conectar a Google Sheets. Los datos no se guardarán automáticamente.")
    sheet = None

# ============================================
# SECCIÓN A - Interpretación clásica
# ============================================
if opcion_menu == "Interpretación clásica":
    st.header("📊 Interpretación clásica de la solución de suelo")

    # ============================================
    # BASE DE DATOS DE ETAPAS (Cultivos)
    # ============================================
    if cultivo_clasico == "Tomate":
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

    if cultivo_clasico == "Pepino":
        etapas = {
            "A": {"dias": "0–10", "descripcion": "Germinación / plántula", "f": 0.3},
            "B": {"dias": "11–20", "descripcion": "Crecimiento vegetativo inicial", "f": 0.5},
            "C": {"dias": "21–35", "descripcion": "Crecimiento vegetativo medio", "f": 0.7},
            "D": {"dias": "36–50", "descripcion": "Floración", "f": 0.9},
            "E": {"dias": "51–65", "descripcion": "Fructificación", "f": 1.0},
        }

    if cultivo_clasico == "Pimiento":
        etapas = {
            "A": {"dias": "0–14", "descripcion": "Plántula", "f": 0.3},
            "B": {"dias": "15–35", "descripcion": "Crecimiento vegetativo", "f": 0.6},
            "C": {"dias": "36–70", "descripcion": "Floración / fruto inicial", "f": 0.85},
            "D": {"dias": "71–100", "descripcion": "Fructificación activa", "f": 1.0},
        }

    if cultivo_clasico == "Fresa":
        etapas = {
            "A": {"dias": "0–14", "descripcion": "Establecimiento", "f": 0.25},
            "B": {"dias": "15–35", "descripcion": "Crecimiento vegetativo", "f": 0.6},
            "C": {"dias": "36–70", "descripcion": "Floración / fruto inicial", "f": 0.85},
            "D": {"dias": "71–100", "descripcion": "Fructificación", "f": 1.0},
        }

    etapa_sel = st.selectbox("Seleccione la etapa fenológica:", list(etapas.keys()))
    f = etapas[etapa_sel]["f"]

    st.info(
        f"**Etapa {etapa_sel}** — {etapas[etapa_sel]['descripcion']} "
        f"({etapas[etapa_sel]['dias']} días) — Factor f = {f}"
    )

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
    N = cols[0].number_input("Nitrógeno (N)", 0.0, key="N_classico")
    P = cols[1].number_input("Fósforo (P)", 0.0, key="P_classico")
    K = cols[2].number_input("Potasio (K)", 0.0, key="K_classico")
    Ca = cols[0].number_input("Calcio (Ca)", 0.0, key="Ca_classico")
    Mg = cols[1].number_input("Magnesio (Mg)", 0.0, key="Mg_classico")
    S = cols[2].number_input("Azufre (S)", 0.0, key="S_classico")
    Fe = cols[0].number_input("Hierro (Fe)", 0.0, key="Fe_classico")
    Mn = cols[1].number_input("Manganeso (Mn)", 0.0, key="Mn_classico")
    Zn = cols[2].number_input("Zinc (Zn)", 0.0, key="Zn_classico")

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
    if volumen_total > 0:
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
            for fert in disp:
                if elem in contenido_fert.get(fert, {}):
                    fert_usado = fert
                    # Convertir ppm a gramos por litro (simplificado)
                    kg_fert = deficit_ppm / contenido_fert[fert][elem] * 1000  # g/L
                    break
            if fert_usado:
                plan.append([elem, deficit_ppm, fert_usado, kg_fert])
            else:
                plan.append([elem, deficit_ppm, "No disponible", 0])

        df_plan = pd.DataFrame(plan, columns=["Elemento", "Déficit (ppm)", "Fertilizante sugerido", "Cantidad (g/L)"])
        st.dataframe(df_plan.style.format({"Déficit (ppm)": "{:.2f}", "Cantidad (g/L)": "{:.2f}"}))

        # ============================================
        # GUARDADO EN GOOGLE SHEETS
        # ============================================
        if sheet:
            try:
                fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                for _, row in df_result.iterrows():
                    sheet.append_row([fecha, cultivo, etapa_sel, row["Elemento"], row["Actual (ppm)"], row["Mínimo"],
                                      row["Máximo"], row["Estado"], row["Diferencia"]])
                st.success("✅ Datos guardados en Google Sheets")
            except Exception as e:
                st.error(f"Error al guardar en Google Sheets: {e}")

# ============================================
# SECCIÓN B - Interpretación con IA
# ============================================

# Diccionarios base (siempre deben definirse antes del if)
valores_ideales = {
    "Tomate": {"N":180, "P":45, "K":275, "Ca":160, "Mg":45, "S":60, "Fe":2, "Mn":0.3, "Zn":0.06},
    "Pepino": {"N":150, "P":40, "K":200, "Ca":120, "Mg":35, "S":50, "Fe":2, "Mn":0.3, "Zn":0.05},
    "Pimiento": {"N":170, "P":50, "K":250, "Ca":150, "Mg":40, "S":55, "Fe":2, "Mn":0.3, "Zn":0.05},
    "Fresa": {"N":160, "P":50, "K":200, "Ca":120, "Mg":35, "S":50, "Fe":2, "Mn":0.3, "Zn":0.05}
}

factores_etapas = {
    "Tomate": {
        "A": {"dias": "0–14", "descripcion": "Establecimiento", "f": 0.25},
        "B": {"dias": "15–28", "descripcion": "Inicio crecimiento vegetativo", "f": 0.45},
        "C": {"dias": "29–42", "descripcion": "Vegetativo medio", "f": 0.65},
        "D": {"dias": "43–56", "descripcion": "Pre-floración / floración temprana", "f": 0.85},
        "E": {"dias": "57–70", "descripcion": "Pico de absorción (crítica)", "f": 1.00},
        "F": {"dias": "71–84", "descripcion": "Fructificación activa", "f": 0.95},
        "G": {"dias": "85–98", "descripcion": "Fructificación avanzada", "f": 0.70},
        "H": {"dias": "99–112+", "descripcion": "Maduración y fin de ciclo", "f": 0.45},
    },
    "Pepino": {
        "A": {"dias": "0–10", "descripcion": "Germinación / plántula", "f": 0.3},
        "B": {"dias": "11–20", "descripcion": "Crecimiento vegetativo inicial", "f": 0.5},
        "C": {"dias": "21–35", "descripcion": "Crecimiento vegetativo medio", "f": 0.7},
        "D": {"dias": "36–50", "descripcion": "Floración", "f": 0.9},
        "E": {"dias": "51–65", "descripcion": "Fructificación", "f": 1.0},
    },
    "Pimiento": {
        "A": {"dias": "0–14", "descripcion": "Plántula", "f": 0.3},
        "B": {"dias": "15–35", "descripcion": "Crecimiento vegetativo", "f": 0.6},
        "C": {"dias": "36–70", "descripcion": "Floración / fruto inicial", "f": 0.85},
        "D": {"dias": "71–100", "descripcion": "Fructificación activa", "f": 1.0},
    },
    "Fresa": {
        "A": {"dias": "0–14", "descripcion": "Establecimiento", "f": 0.25},
        "B": {"dias": "15–35", "descripcion": "Crecimiento vegetativo", "f": 0.6},
        "C": {"dias": "36–70", "descripcion": "Floración / fruto inicial", "f": 0.85},
        "D": {"dias": "71–100", "descripcion": "Fructificación", "f": 1.0},
    }
}

# ============================================
# Bloque IA
# ============================================
if opcion_menu == "Interpretación con IA":
    st.header("🤖 Interpretación inteligente (IA) de la nutrición vegetal")

    # Selección de cultivo y etapa
    cultivo_ia = st.selectbox("Seleccione el cultivo:", list(factores_etapas.keys()))
    etapa_sel_ia = st.selectbox(
        "Seleccione la etapa fenológica:",
        list(factores_etapas[cultivo_ia].keys())
    )

    f = factores_etapas[cultivo_ia][etapa_sel_ia]["f"]
    valores_base = valores_ideales[cultivo_ia]
    valores_ajustados = {k: v*f for k, v in valores_base.items()}

    # Crear rango ±10
    rango_valores = {k: (v*0.9, v*1.1) for k, v in valores_ajustados.items()}  # ±10%

    # Inputs de usuario
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

    data_usuario = {"N": N, "P": P, "K": K, "Ca": Ca, "Mg": Mg, "S": S, "Fe": Fe, "Mn": Mn, "Zn": Zn}

    # Comparación con valores ajustados por etapa
    resultados = []
    for elem, valor in data_usuario.items():
        min_val, max_val = rango_valores.get(elem, (np.nan, np.nan))
        if valor < min_val:
            estado = "Déficit"
            diff = min_val - valor
        elif valor > max_val:
            estado = "Exceso"
            diff = valor - max_val
        else:
            estado = "Óptimo"
            diff = 0
        resultados.append([elem, valor, min_val, max_val, estado, diff])

    df_result = pd.DataFrame(resultados, columns=["Elemento", "Actual (ppm)", "Mínimo (ppm)", "Máximo (ppm)", "Estado", "Diferencia"])

    # Formatear columnas numéricas
    numeric_cols = ["Actual (ppm)", "Mínimo (ppm)", "Máximo (ppm)", "Diferencia"]
    def format_numeric(x):
        if pd.isna(x):
            return ""
        else:
            return f"{x:.2f}"
    st.dataframe(df_result.style.format({col: format_numeric for col in numeric_cols}))

    # Guardado en Google Sheets
    if sheet:
        fila = [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), cultivo_ia, etapa_sel_ia, "IA"] + [data_usuario[e] for e in data_usuario]
        try:
            sheet.append_row(fila)
            st.success("✅ Datos guardados en Google Sheets")
        except Exception as e:
            st.warning(f"No se pudieron guardar los datos: {e}")
