# Analizador Bar by Bar

Versión inicial del analizador de **cualquier vela** a partir de las velas descargadas de IQ Option.

## Funcionamiento

1. Ingresa las credenciales de IQ Option, elige activo, marco temporal y número de velas y descarga los datos.
2. En el analizador selecciona **fecha, hora y minuto (horario de Ciudad de México)**. Las listas muestran únicamente horas y minutos existentes en las velas descargadas.
3. Se muestran el **cierre anterior**, el **OPEN** y el **CLOSE** de la vela elegida.
4. Revisa las vistas **Todo**, **Antes**, **Inicio** (vela truncada al precio OPEN) y **Fin** (vela completa).
5. Activa ADX estándar, ADX-MC, ambos o ninguno; ajusta periodo y evaluación MC; elige fondo blanco o negro. Los paneles mantienen líneas horizontales en 20, 35 (morado) y 50.
6. Genera un PDF tamaño **carta, vertical, tres páginas**: pág. 1 Todo y Antes (ADX estándar); pág. 2 Inicio y Fin (ADX estándar); pág. 3 Inicio y Fin (ADX-MC).

No se buscan patrones JAPY2 ni se dibujan triángulos. El cálculo interno de algunas medias permanece para mantener compatibilidad con las gráficas de la versión base.

## Archivos

`app.py`, `charts.py`, `iqoption_service.py`, `japy2.py`, `pdf_report.py`, `requirements.txt`.

## Ejecutar

Instala dependencias con `pip install -r requirements.txt` y ejecuta `streamlit run app.py`. Requiere conexión para obtener velas de IQ Option.
