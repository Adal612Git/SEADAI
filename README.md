# SEADAI
(Sistema Estomacal Autónomo de Diagnóstico y Análisis Inteligente Plus Ultra) 🔧 ¿Qué hará? Un sistema que, con tus datos:  Detecta patrones digestivos.  Predice síntomas por alimento/emoción.  Sugiere dietas de recuperación.  Te da alertas y semáforos en tiempo real.

## Uso rapido

1. Restaura la base de datos MySQL ejecutando:
   ```bash
   mysql -u root -p -e "CREATE DATABASE salud;"
   mysql -u root -p salud < salud_dump.sql
   ```
2. Establece las variables de entorno `SEADAI_USER` y `SEADAI_PWD` para la conexion (opcional si usas `root`/`password`).
3. Ejecuta `python3 run_all.py` para generar el PDF, entrenar el modelo y crear las recomendaciones.

Todos los resultados pueden compartirse con el gastroenterologo para un mejor seguimiento.
