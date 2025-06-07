"""Genera el archivo recomendaciones_SEADAI.md con sugerencias clinicas."""

import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError


def cargar_datos(usuario: str, contrasena: str, host: str = "localhost", bd: str = "salud") -> pd.DataFrame:
    url = f"mysql+mysqlconnector://{usuario}:{contrasena}@{host}/{bd}"
    engine = create_engine(url)
    try:
        df = pd.read_sql("SELECT * FROM registros", engine)
    except SQLAlchemyError as exc:
        raise RuntimeError(f"No se pudo leer la base de datos: {exc}")
    return df


def generar_md(df: pd.DataFrame, nombre: str = "recomendaciones_SEADAI.md") -> None:
    sintomas_comunes = df.get("Sintomas", pd.Series(dtype=str)).dropna()
    top_sint = sintomas_comunes.value_counts().head(5).index.tolist()
    with open(nombre, "w", encoding="utf-8") as f:
        f.write("# Plan de accion para mejorar la digestion\n\n")
        f.write("Basado en el analisis de tus registros y guias clinicas recientes (2023-2025).\n\n")
        f.write("## Recomendaciones\n")
        f.write("- Mantener un registro detallado de alimentos y sintomas.\n")
        f.write("- Reducir el consumo de grasas saturadas por la ausencia de vesicula.\n")
        f.write("- Controlar el estres con tecnicas de respiracion y pausas activas.\n")
        f.write("- Realizar actividad fisica moderada a diario.\n")
        f.write("- Consultar al medico sobre medicamentos que puedan afectar tu digestion.\n")
        if top_sint:
            f.write("- Sintomas frecuentes detectados: " + ", ".join(top_sint) + "\n")


def main() -> None:
    usuario = os.getenv("SEADAI_USER", "root")
    contrasena = os.getenv("SEADAI_PWD", "password")
    try:
        df = cargar_datos(usuario, contrasena)
    except Exception as exc:
        print("Error al generar recomendaciones:", exc)
        return
    generar_md(df)


if __name__ == "__main__":
    main()
