"""Ejecuta todo el flujo de analisis y generacion de reportes."""

import analisis_seadai
import predictor_sintomas
import generar_recomendaciones


def main() -> None:
    analisis_seadai.main()
    predictor_sintomas.entrenar_guardar()
    generar_recomendaciones.main()


if __name__ == "__main__":
    main()
