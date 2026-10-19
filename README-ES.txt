SPELLING BEE — APLICACIÓN WEB
============================

CONTENIDO
- index.html: aplicación web con las 20 ruletas y las listas incluidas.
- respaldo-spelling-bee-ruletas.json: respaldo original de las listas.
- audio_manifest.json: relación de palabras y archivos MP3.
- generar_audios.py: generador de audios en lote.
- requirements.txt: dependencia de Python para generar voz.
- audio/: aquí se guardan los MP3 generados.

PASO 1 — GENERAR LOS MP3 EN WINDOWS
1. Instala Python 3.10 o posterior si todavía no lo tienes.
2. Abre la carpeta spelling-bee-web en el Explorador de archivos.
3. Haz clic en la barra de dirección, escribe powershell y pulsa Enter.
4. Ejecuta estos comandos, uno por uno:

   py -m venv .venv
   .\.venv\Scripts\python.exe -m pip install --upgrade pip
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   .\.venv\Scripts\python.exe generar_audios.py

El generador usa la voz en-US-AriaNeural (femenina, inglés estadounidense) a través de Edge TTS.
Necesita internet durante la generación. Genera 428 archivos para las palabras únicas de las listas.
Si se interrumpe, vuelve a ejecutar el último comando: los MP3 ya generados se omiten.
La disponibilidad y las condiciones del servicio de voz pueden cambiar; no es una API oficial
con garantía de disponibilidad. Verifica los términos del servicio antes de usos de gran escala.

PASO 2 — PROBAR LOCALMENTE
Abre index.html en Chrome o Edge. Gira una ruleta y comprueba el audio. Para comprobar de forma
más fiable el comportamiento de rutas de archivos, también puedes usar un servidor local:

   .\.venv\Scripts\python.exe -m http.server 8000

Luego abre http://localhost:8000 en el navegador. Para detenerlo, vuelve a PowerShell y pulsa Ctrl+C.

PASO 3 — PUBLICAR GRATIS EN GITHUB PAGES
1. Crea o inicia sesión en https://github.com/.
2. Crea un repositorio público, por ejemplo spelling-bee.
3. Sube el archivo index.html, la carpeta audio completa y, si quieres, el JSON de respaldo.
   No es necesario subir .venv ni la carpeta __pycache__ si aparecen.
4. En el repositorio abre Settings > Pages.
5. En Build and deployment selecciona Deploy from a branch.
6. Selecciona la rama main y la carpeta /(root), y guarda.
7. Espera a que GitHub Pages publique el sitio. La dirección tendrá el formato:
   https://TU-USUARIO.github.io/spelling-bee/

IMPORTANTE
- Debes subir los MP3 dentro de la carpeta audio conservando sus nombres numéricos.
- Si solo subes index.html, la ruleta funcionará, pero no estarán disponibles los MP3; la aplicación
  intentará usar como alternativa la voz del navegador.
- Las modificaciones que los usuarios hagan en el editor se guardan en su propio navegador y no
  actualizan la página pública para los demás.
- Conserva el JSON de respaldo en un lugar seguro.

AUDIO COMPLETO DE LAS LISTAS PRINCIPALES
----------------------------------------
Si ya generaste los MP3 individuales de las palabras, puedes unirlos en un único audio que recorre las listas principales por grado y omite las listas cuyo nombre contiene “final round”. El audio anuncia cada grado en inglés y deja una pausa entre palabras.

1. Instala FFmpeg en Windows (solo una vez). En PowerShell ejecuta:
   winget install --id Gyan.FFmpeg.Shared -e
   Cuando termine, cierra y vuelve a abrir PowerShell.
2. En la carpeta del proyecto, instala las dependencias:
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
3. Ejecuta:
   .\.venv\Scripts\python.exe crear_audio_completo.py
4. El resultado estará en:
   spelling-bee-todas-las-palabras.mp3

El script usa las palabras en el orden del respaldo, conserva repeticiones si una palabra aparece en varios grados, y omite las ruletas “final round” y las ruletas vacías. Si avisa que faltan audios, ejecuta primero generar_audios.py y vuelve a ejecutar crear_audio_completo.py.

AUDIO DE PRÁCTICA POR GRADO (LISTA REGULAR + FINAL ROUND)
---------------------------------------------------------
El respaldo contiene 816 apariciones de palabras entre las 12 listas llenas, porque algunas palabras
se repiten entre grados y rondas. Hay 428 palabras únicas, por lo que deben existir 428 MP3 individuales.
Si el generador terminó con 425, significa que faltan tres archivos: no es que la web tenga 391 palabras
extra. Vuelve a ejecutar generar_audios.py; omite los audios ya existentes y reintenta los que faltan.

Cuando la generación indique que todos están listos:
1. Asegúrate de tener FFmpeg instalado (ver el paso anterior).
2. Ejecuta:
   .\.venv\Scripts\python.exe crear_audios_por_grado.py
3. Se creará la carpeta audios_por_grado con seis archivos MP3 (Sixth grade a Eleventh grade), cada uno
   con su lista normal seguida de su lista “final round”. También se creará el audio maestro
   spelling-bee-todos-los-grados.mp3 con todos los grados consecutivos.
4. El script verifica los audios individuales antes de unirlos y muestra cuáles faltan si todavía hay
   archivos ausentes.

Para publicar la web, sube index.html y la carpeta audio/ con los MP3 numéricos. Los audios largos de
práctica son archivos aparte; puedes compartirlos por Google Drive u otro servicio, o añadirlos al
repositorio si el tamaño total es razonable. No hace falta subir los scripts de Python para que la web
funcione.
