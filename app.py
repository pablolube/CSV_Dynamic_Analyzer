import streamlit as st
import pandas as pd

# === CONFIGURACIÓN GENERAL ===
st.set_page_config(page_title="Fusionador y Analizador de Datos", layout="wide")
st.title("📊 Fusionador y Analizador Dinámico de Archivos")

st.write("""
Subí tus archivos **CSV o Excel (.xlsx)**.  
El programa los leerá, los unirá automáticamente por columnas comunes y permitirá analizarlos dinámicamente.
""")

# Subida de archivos
uploaded_files = st.file_uploader(
    "Subí tus archivos CSV o Excel", type=["csv", "xlsx"], accept_multiple_files=True
)

if uploaded_files:
    dfs = []
    for uploaded_file in uploaded_files:
        try:
            if uploaded_file.name.endswith(".csv"):
                # Leemos el contenido como string
                content = uploaded_file.getvalue().decode("utf-8", errors="ignore")
                
                # Detectamos el delimitador automáticamente
                sample = content.splitlines()[0]
                dialect = csv.Sniffer().sniff(sample)
                
                # Convertimos a StringIO y leemos con pandas
                df = pd.read_csv(io.StringIO(content), sep=dialect.delimiter, low_memory=False, on_bad_lines='skip')
            else:
                df = pd.read_excel(uploaded_file)
            
            dfs.append(df)
            st.write(f"✅ Archivo leído: {uploaded_file.name} ({len(df)} filas)")
        except Exception as e:
            st.error(f"❌ Error al leer {uploaded_file.name}: {e}")

    # Verificamos que haya al menos un DataFrame
    if not dfs:
        st.stop()

    # Unión automática por columnas comunes
    if len(dfs) > 1:
        common_cols = list(set.intersection(*(set(df.columns) for df in dfs)))
        if not common_cols:
            st.error("❌ No hay columnas comunes entre los archivos.")
            merged_df = None
        else:
            st.write("Columnas comunes detectadas:", common_cols)
            merged_df = dfs[0]
            for df in dfs[1:]:
                merged_df = pd.merge(merged_df, df, on=common_cols, how="outer")
    else:
        merged_df = dfs[0]
        
    # === 3️⃣ Previsualización del DataFrame combinado ===
    if merged_df is not None:
        st.write("### 📋 Previsualización del DataFrame combinado")
        st.dataframe(merged_df.head(20))

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
