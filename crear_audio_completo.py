"""Une en un solo MP3 las palabras de las ruletas principales por grado.
Omite automáticamente cualquier lista cuyo nombre contenga 'final round'.
Usa los MP3 individuales ya generados en la carpeta audio/.
"""
import asyncio
import json
import shutil
import tempfile
from pathlib import Path

from pydub import AudioSegment
import edge_tts

ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "respaldo-spelling-bee-ruletas.json"
MANIFEST_FILE = ROOT / "audio_manifest.json"
AUDIO_DIR = ROOT / "audio"
OUTPUT_FILE = ROOT / "spelling-bee-todas-las-palabras.mp3"
VOICE = "en-US-AriaNeural"
WORD_PAUSE_MS = 700
GRADE_PAUSE_MS = 1800

async def create_label(text, target):
    await edge_tts.Communicate(text, VOICE).save(str(target))

def main():
    if not shutil.which("ffmpeg") and not shutil.which("avconv"):
        raise SystemExit(
            "No encuentro FFmpeg. Instálalo y vuelve a abrir PowerShell.\n"
            "En Windows puedes probar: winget install --id Gyan.FFmpeg.Shared -e"
        )

    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
    lists = [item for item in data.get("lists", [])
             if item.get("words") and "final round" not in item.get("name", "").lower()]
    if not lists:
        raise SystemExit("No encontré listas principales con palabras en el archivo JSON.")

    missing = []
    total_words = sum(len(item.get("words", [])) for item in lists)
    print("Listas que se incluirán:")
    for item in lists:
        print(f"  - {item['name']}: {len(item.get('words', []))} palabras")
    print(f"Total de apariciones de palabras (incluye repeticiones entre grados): {total_words}")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        combined = AudioSegment.empty()
        completed = 0

        for grade_index, item in enumerate(lists):
            grade_name = item["name"]
            label_path = temp_path / f"grade_{grade_index}.mp3"
            print(f"\nPreparando sección: {grade_name}")
            try:
                asyncio.run(create_label(grade_name, label_path))
                combined += AudioSegment.from_mp3(label_path) + AudioSegment.silent(duration=GRADE_PAUSE_MS)
            except Exception as exc:
                print(f"Aviso: no pude generar el título hablado de {grade_name}: {exc}")

            for word in item.get("words", []):
                key = str(word).strip().lower()
                entry = manifest.get(key)
                if not entry:
                    missing.append(word)
                    continue
                clip_path = AUDIO_DIR / entry["file"]
                if not clip_path.exists() or clip_path.stat().st_size < 500:
                    missing.append(word)
                    continue
                try:
                    clip = AudioSegment.from_mp3(clip_path)
                    combined += clip + AudioSegment.silent(duration=WORD_PAUSE_MS)
                    completed += 1
                    if completed % 50 == 0:
                        print(f"  Procesadas {completed}/{total_words} palabras...")
                except Exception as exc:
                    print(f"Error leyendo el audio de '{word}': {exc}")
                    missing.append(word)
            combined += AudioSegment.silent(duration=GRADE_PAUSE_MS * 2)

        if completed == 0:
            raise SystemExit("No pude incorporar audios. Revisa que los MP3 estén dentro de la carpeta audio.")
        combined.export(OUTPUT_FILE, format="mp3", bitrate="128k")

    print("\n¡Audio completo creado!")
    print(f"Archivo: {OUTPUT_FILE}")
    print(f"Palabras incorporadas: {completed}/{total_words}")
    if missing:
        print("\nEstas palabras no se incluyeron porque falta su MP3 o su entrada en el manifiesto:")
        for word in missing:
            print(f"  - {word}")
        print("Vuelve a ejecutar generar_audios.py y después este script.")
    else:
        print("Todas las palabras de las listas principales están incluidas.")

if __name__ == "__main__":
    main()
