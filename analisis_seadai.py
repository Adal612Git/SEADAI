"""Analisis de la base de datos digestiva y generacion de reportes clinicos."""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sklearn.cluster import KMeans
from wordcloud import WordCloud
from fpdf import FPDF


def cargar_datos(usuario: str, contrasena: str, host: str = "localhost", bd: str = "salud") -> pd.DataFrame:
    """Carga la tabla registros de MySQL a un DataFrame."""
    url = f"mysql+mysqlconnector://{usuario}:{contrasena}@{host}/{bd}"
    engine = create_engine(url)
    query = "SELECT * FROM registros"
    try:
        df = pd.read_sql(query, engine)
    except SQLAlchemyError as exc:
        raise RuntimeError(f"No se pudo leer la base de datos: {exc}")
    if df.empty:
        raise RuntimeError("La tabla registros esta vacia")
    return df


def analizar(df: pd.DataFrame) -> dict:
    """Realiza analisis basicos y genera graficas."""
    if not os.path.exists("graficas"):
        os.mkdir("graficas")

    resultado = {"correlaciones": {}, "clusters": {}}

    if "Tipo_de_evacuacion" in df.columns and "Alimentos" in df.columns:
        df["Bristol6_7"] = df["Tipo_de_evacuacion"].isin([6, 7]).astype(int)
        alimentos = df["Alimentos"].str.get_dummies(sep=", ")
        corr = alimentos.corrwith(df["Bristol6_7"]).sort_values(ascending=False)
        resultado["correlaciones"] = corr.to_dict()
        plt.figure(figsize=(10, 6))
        sns.barplot(x=corr.values, y=corr.index, palette="viridis")
        plt.title("Alimentos relacionados con evacuaciones Bristol 6-7")
        plt.xlabel("Correlacion")
        plt.tight_layout()
        plt.savefig("graficas/alimentos_bristol.png")
        plt.close()

    if "Sintomas" in df.columns:
        text_sintomas = " ".join(df["Sintomas"].dropna().astype(str))
        if text_sintomas:
            wc = WordCloud(background_color="white").generate(text_sintomas)
            plt.imshow(wc, interpolation="bilinear")
            plt.axis("off")
            plt.tight_layout()
            plt.savefig("graficas/nube_sintomas.png")
            plt.close()

    # Cluster de dias basado en sintomas y emociones
    cols = {"sint_len": df.get("Sintomas", pd.Series(dtype=str)).fillna("").str.len(),
            "emo_len": df.get("Diario_Emocional", pd.Series(dtype=str)).fillna("").str.len(),
            "bristol": df.get("Tipo_de_evacuacion", pd.Series(dtype=float)).fillna(0)}
    features = pd.DataFrame(cols)
    try:
        kmeans = KMeans(n_clusters=2, random_state=42)
        df["cluster"] = kmeans.fit_predict(features)
        resultado["clusters"] = df["cluster"].value_counts().to_dict()
        plt.figure(figsize=(8,4))
        sns.scatterplot(x="sint_len", y="bristol", hue="cluster", data=df, palette="Set2")
        plt.title("Clustering de dias")
        plt.tight_layout()
        plt.savefig("graficas/clusters.png")
        plt.close()
    except Exception:
        pass

    # Grafico de progreso temporal
    if "Fecha" in df.columns and "Tipo_de_evacuacion" in df.columns:
        df_fecha = pd.to_datetime(df["Fecha"], errors="coerce")
        ordenado = df.sort_values("Fecha")
        plt.figure(figsize=(10,4))
        sns.lineplot(x=df_fecha, y=df["Tipo_de_evacuacion"], marker="o")
        plt.ylabel("Escala de Bristol")
        plt.title("Progreso temporal")
        plt.tight_layout()
        plt.savefig("graficas/progreso_temporal.png")
        plt.close()

    return resultado


def generar_pdf(resumen: dict, nombre: str = "reporte_SEADAI.pdf") -> None:
    """Crea un PDF clinico con resumen y graficas."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Reporte Clinico SEADAI", ln=1, align="C")
    pdf.ln(5)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 8, "Diagnostico basado en patrones encontrados en la base de datos digestiva.")
    pdf.ln(5)

    if resumen.get("correlaciones"):
        pdf.cell(0, 8, "Riesgos detectados:", ln=1)
        for k, v in resumen["correlaciones"].items():
            if v > 0.3:
                pdf.cell(0, 8, f"- {k}: correlacion {v:.2f}", ln=1)
        pdf.ln(5)

    pdf.cell(0, 8, "Recomendaciones personalizadas al final del documento.", ln=1)

    graficas = [
        "alimentos_bristol.png",
        "nube_sintomas.png",
        "clusters.png",
        "progreso_temporal.png",
    ]
    for graf in graficas:
        ruta = os.path.join("graficas", graf)
        if os.path.exists(ruta):
            pdf.add_page()
            pdf.image(ruta, w=180)

    pdf.output(nombre)


def main():
    """Ejecuta todo el flujo de trabajo."""
    usuario = os.getenv("SEADAI_USER", "root")
    contrasena = os.getenv("SEADAI_PWD", "password")
    try:
        df = cargar_datos(usuario, contrasena)
    except Exception as exc:
        print("Error al conectar a la base de datos:", exc)
        return
    resumen = analizar(df)
    generar_pdf(resumen)
    df.to_csv("registros_export.csv", index=False)


if __name__ == "__main__":
    main()
