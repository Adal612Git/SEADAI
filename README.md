# SEADAI
(Sistema Estomacal Autónomo de Diagnóstico y Análisis Inteligente Plus Ultra) 🔧 ¿Qué hará? Un sistema que, con tus datos:  Detecta patrones digestivos.  Predice síntomas por alimento/emoción.  Sugiere dietas de recuperación.  Te da alertas y semáforos en tiempo real.

## Uso rapido

1. Restaura la base de datos MySQL ejecutando:
   ```bash
   mysql -u root -p -e "CREATE DATABASE SEADAI;"
   mysql -u root -p SEADAI < salud_dump.sql
   ```
2. Establece las variables de entorno `SEADAI_USER` y `SEADAI_PWD` para la conexion.
3. Ejecuta `python3 analisis_seadai.py` para generar `reporte_SEADAI.pdf` y las graficas en la carpeta `graficas/`.
4. Ejecuta `python3 predictor_sintomas.py` para entrenar el modelo de prediccion y guardar `modelo_sintomas.pkl`.

Todos los resultados pueden compartirse con el gastroenterologo para un mejor seguimiento.
