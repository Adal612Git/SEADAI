"""Modelo sencillo para predecir sintomas futuros basado en datos historicos."""

import os
import pandas as pd
from sqlalchemy import create_engine
main
    return df


def preparar_datos(df: pd.DataFrame):
    df = df.copy()
main
    X = df[["Tipo_de_evacuacion"]].fillna(0)
    y = df["Sintomas_bin"]
    return train_test_split(X, y, test_size=0.2, random_state=42)


def entrenar_guardar(usuario="root", contrasena="password"):
main
    X_train, X_test, y_train, y_test = preparar_datos(df)
    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    print(classification_report(y_test, preds))
main
    joblib.dump(model, "modelo_sintomas.pkl")


if __name__ == "__main__":
    user = os.getenv("SEADAI_USER", "root")
    pwd = os.getenv("SEADAI_PWD", "password")
    entrenar_guardar(user, pwd)
