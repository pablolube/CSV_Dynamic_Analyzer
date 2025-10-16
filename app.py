import streamlit as st
import pandas as pd
import os

# === CONFIGURACIÓN GENERAL ===
st.set_page_config(page_title="Fusionador y Analizador de Datos", layout="wide")
st.title("📊 Fusionador y Analizador Dinámico de Archivos (Carpeta Local)")

st.write("""
Indicá una carpeta en tu computadora que contenga archivos **CSV o Excel (.xlsx)**.
El programa los leerá directamente, los unirá por columnas comunes y permitirá analizarlos dinámicamente.
""")

# === 1️⃣ Ingreso de la carpeta ===
folder_path = st.text_input("📂 Ingresá la ruta de la carpeta (por ejemplo: C:\\\\MisDatos o /home/usuario/datos):")

if folder_path:
    if not os.path.exists(folder_path):
        st.error("❌ La ruta indicada no existe. Verificá que sea correcta.")
    else:
        # Listar archivos CSV y Excel en la carpeta
        files = [f for f in os.listdir(folder_path) if f.endswith((".csv", ".xlsx"))]

        if not files:
            st.warning("No se encontraron archivos CSV ni Excel en esa carpeta.")
        else:
            st.success(f"Se encontraron {len(files)} archivos: {', '.join(files)}")

            # === 2️⃣ Lectura de archivos ===
            dfs = []
            for file_name in files:
                file_path = os.path.join(folder_path, file_name)
                try:
                    if file_name.endswith(".csv"):
                        df = pd.read_csv(file_path, sep=';', low_memory=False, on_bad_lines='skip')
                    else:
                        df = pd.read_excel(file_path)
                    dfs.append(df)
                    st.write(f"✅ Archivo leído: {file_name} ({len(df)} filas)")
                except Exception as e:
                    st.error(f"Error al leer {file_name}: {e}")

            # === 3️⃣ Unión automática por columnas comunes ===
            if len(dfs) > 1:
                common_cols = list(set.intersection(*(set(df.columns) for df in dfs)))
                if not common_cols:
                    st.error("No hay columnas comunes entre los archivos.")
                else:
                    st.write("Columnas comunes detectadas:", common_cols)
                    merged_df = dfs[0]
                    for df in dfs[1:]:
                        merged_df = pd.merge(merged_df, df, on=common_cols, how="outer")
            else:
                merged_df = dfs[0]

            # === 4️⃣ Previsualización del DataFrame combinado ===
            st.write("### 📋 Previsualización del DataFrame combinado")
            st.dataframe(merged_df.head(20))

# === 5️⃣ Tabla dinámica interactiva ===
if 'merged_df' in locals():
    st.sidebar.header("⚙️ Tabla Dinámica Interactiva")

    all_cols = merged_df.columns.tolist()

    # Selección de filas (agrupamiento)
    rows = st.sidebar.multiselect("Seleccioná columnas para filas", all_cols)

    # Selección de columnas de valores
    values = st.sidebar.multiselect("Seleccioná columnas para valores", all_cols)

    # Función de agregación
    aggfunc = st.sidebar.selectbox(
        "Función de agregación",
        ["sum", "mean", "count", "max", "min"]
    )

    if values and rows:
        # Crear tabla dinámica
        pivot = pd.pivot_table(
            merged_df,
            index=rows,
            values=values,
            aggfunc=aggfunc,
            fill_value=0
        ).reset_index()

        st.write("### 🔍 Resultado de la tabla dinámica")
        st.dataframe(pivot)

        # Botón para descargar
        csv = pivot.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Descargar tabla dinámica como CSV",
            data=csv,
            file_name="tabla_dinamica.csv",
            mime="text/csv"
        )
    else:
        st.info("Seleccioná al menos una columna para filas y una columna para valores para generar la tabla dinámica.")
