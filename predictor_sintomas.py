"""Modelo sencillo para predecir sintomas futuros basado en datos historicos."""

import os
import pandas as pd
from sqlalchemy import create_engine
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report


def cargar_datos(usuario: str, contrasena: str, host: str = "localhost", bd: str = "SEADAI") -> pd.DataFrame:
    url = f"mysql+mysqlconnector://{usuario}:{contrasena}@{host}/{bd}"
    engine = create_engine(url)
    df = pd.read_sql("SELECT * FROM registros", engine)
    return df


def preparar_datos(df: pd.DataFrame):
    df = df.copy()
    df["Sintomas_bin"] = df["Sintomas"].notna().astype(int)
    X = df[["Tipo_de_evacuacion"]].fillna(0)
    y = df["Sintomas_bin"]
    return train_test_split(X, y, test_size=0.2, random_state=42)


def entrenar_guardar(usuario="root", contrasena="password"):
    df = cargar_datos(usuario, contrasena)
    X_train, X_test, y_train, y_test = preparar_datos(df)
    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    print(classification_report(y_test, preds))
    import joblib
    joblib.dump(model, "modelo_sintomas.pkl")


if __name__ == "__main__":
    user = os.getenv("SEADAI_USER", "root")
    pwd = os.getenv("SEADAI_PWD", "password")
    entrenar_guardar(user, pwd)
