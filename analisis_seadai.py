"""Analisis de la base de datos SEADAI y generacion de reportes clinicos."""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from sklearn.cluster import KMeans
from wordcloud import WordCloud
from fpdf import FPDF


def cargar_datos(usuario: str, contrasena: str, host: str = "localhost", bd: str = "SEADAI") -> pd.DataFrame:
    """Carga la tabla registros de MySQL a un DataFrame."""
    url = f"mysql+mysqlconnector://{usuario}:{contrasena}@{host}/{bd}"
    engine = create_engine(url)
    query = "SELECT * FROM registros"
    df = pd.read_sql(query, engine)
    return df


def analizar(df: pd.DataFrame) -> dict:
    """Realiza analisis basicos y genera graficas."""
    if not os.path.exists("graficas"):
        os.mkdir("graficas")

    # Correlacion alimentos vs evacuaciones Bristol 6 y 7
    df["Bristol6_7"] = df["Tipo_de_evacuacion"].isin([6, 7]).astype(int)
    alimentos = df["Alimentos"].str.get_dummies(sep=", ")
    corr = alimentos.corrwith(df["Bristol6_7"]).sort_values(ascending=False)
    plt.figure(figsize=(10, 6))
    sns.barplot(x=corr.values, y=corr.index, palette="viridis")
    plt.title("Alimentos relacionados con evacuaciones Bristol 6-7")
    plt.xlabel("Correlacion")
    plt.tight_layout()
    plt.savefig("graficas/alimentos_bristol.png")
    plt.close()

    # Nube de palabras de sintomas
    text_sintomas = " ".join(df["Sintomas"].dropna().astype(str))
    wc = WordCloud(background_color="white").generate(text_sintomas)
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig("graficas/nube_sintomas.png")
    plt.close()

    # Cluster de dias buenos vs malos basado en sintomas y emociones
    sint = df["Sintomas"].fillna("")
    emo = df["Diario_Emocional"].fillna("")
    features = pd.DataFrame({
        "sint_len": sint.str.len(),
        "emo_len": emo.str.len(),
        "bristol": df["Tipo_de_evacuacion"].fillna(0)
    })
    kmeans = KMeans(n_clusters=2, random_state=42)
    df["cluster"] = kmeans.fit_predict(features)
    plt.figure(figsize=(8,4))
    sns.scatterplot(x="sint_len", y="bristol", hue="cluster", data=df, palette="Set2")
    plt.title("Clustering de dias")
    plt.tight_layout()
    plt.savefig("graficas/clusters.png")
    plt.close()

    return {
        "correlaciones": corr.to_dict(),
        "clusters": df["cluster"].value_counts().to_dict(),
    }


def generar_pdf(resumen: dict, nombre="reporte_SEADAI.pdf") -> None:
    """Crea un PDF clinico con resumen y graficas."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Reporte Clinico SEADAI", ln=1, align="C")
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, "Diagnostico basado en patrones y correlaciones detectadas.")
    pdf.ln(5)
    pdf.cell(0,10, "Riesgos detectados:", ln=1)
    for k,v in resumen["correlaciones"].items():
        if v > 0.3:
            pdf.cell(0,10, f"- {k}: correlacion {v:.2f}", ln=1)
    pdf.ln(5)
    pdf.cell(0,10, "Recomendaciones personalizadas al final del documento.", ln=1)
    for graf in ["alimentos_bristol.png", "nube_sintomas.png", "clusters.png"]:
        pdf.add_page()
        pdf.image(os.path.join("graficas", graf), w=180)
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
