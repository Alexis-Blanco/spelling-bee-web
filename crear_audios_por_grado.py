"""Crea un MP3 por grado con la lista regular + final round y un audio maestro.
Requiere los MP3 individuales de audio/ y FFmpeg instalado en Windows.
"""
import asyncio
import json
import shutil
import tempfile
from pathlib import Path

import edge_tts
from pydub import AudioSegment

ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "respaldo-spelling-bee-ruletas.json"
MANIFEST_FILE = ROOT / "audio_manifest.json"
AUDIO_DIR = ROOT / "audio"
OUTPUT_DIR = ROOT / "audios_por_grado"
VOICE = "en-US-AriaNeural"
WORD_PAUSE_MS = 800
SECTION_PAUSE_MS = 1800
GRADE_PAUSE_MS = 3000
GRADE_ORDER = [
    "sixth grade", "seventh grade", "eighth grade",
    "ninth grade", "tenth grade", "eleventh grade",
]

async def make_spoken_label(text: str, target: Path):
    await edge_tts.Communicate(text, VOICE).save(str(target))

def normalized(value):
    return " ".join(str(value).strip().lower().split())

def main():
    if not shutil.which("ffmpeg") and not shutil.which("avconv"):
        raise SystemExit(
            "No encuentro FFmpeg. En PowerShell ejecuta:\n"
            "winget install --id Gyan.FFmpeg.Shared -e\n"
            "Cuando termine, cierra y vuelve a abrir PowerShell."
        )

    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
    source_lists = [x for x in data.get("lists", []) if x.get("words")]
    by_name = {normalized(x.get("name", "")): x for x in source_lists}

    grade_pairs = []
    for grade in GRADE_ORDER:
        main_list = by_name.get(grade)
        final_list = by_name.get(grade + " final round")
        if not main_list and not final_list:
            print(f"Aviso: no encontré listas para {grade.title()}.")
            continue
        grade_pairs.append((grade, main_list, final_list))

    if not grade_pairs:
        raise SystemExit("No encontré listas de grados en el JSON.")

    missing = []
    for grade, main_list, final_list in grade_pairs:
        for item in (main_list, final_list):
            if not item:
                continue
            for word in item.get("words", []):
                entry = manifest.get(normalized(word))
                path = AUDIO_DIR / entry["file"] if entry else None
                if not path or not path.is_file() or path.stat().st_size < 500:
                    missing.append((grade.title(), word))

    total_occurrences = sum(len(item.get("words", [])) for _, a, b in grade_pairs for item in (a, b) if item)
    if missing:
        print(f"Faltan audios para {len(missing)} apariciones de palabras (puede haber repetidas):")
        seen = set()
        for grade, word in missing:
            key = normalized(word)
            if key not in seen:
                print(f"  - {word} ({grade})")
                seen.add(key)
        print("\nPrimero ejecuta: .\\.venv\\Scripts\\python.exe generar_audios.py")
        print("Después vuelve a ejecutar este script.")
        raise SystemExit(1)

    OUTPUT_DIR.mkdir(exist_ok=True)
    master = AudioSegment.empty()
    total_done = 0

    with tempfile.TemporaryDirectory() as temp:
        temp_dir = Path(temp)
        for index, (grade, main_list, final_list) in enumerate(grade_pairs):
            grade_audio = AudioSegment.empty()
            sections = [(main_list, grade.title()), (final_list, (grade + " final round").title())]
            for section_index, (item, label) in enumerate(sections):
                if not item:
                    continue
                label_path = temp_dir / f"label_{index}_{section_index}.mp3"
                try:
                    asyncio.run(make_spoken_label(label, label_path))
                    grade_audio += AudioSegment.from_mp3(label_path) + AudioSegment.silent(duration=SECTION_PAUSE_MS)
                except Exception as exc:
                    raise SystemExit(f"No pude generar el título hablado '{label}': {exc}")

                for word in item.get("words", []):
                    entry = manifest[normalized(word)]
                    clip = AudioSegment.from_mp3(AUDIO_DIR / entry["file"])
                    grade_audio += clip + AudioSegment.silent(duration=WORD_PAUSE_MS)
                    total_done += 1
                grade_audio += AudioSegment.silent(duration=SECTION_PAUSE_MS)

            out_file = OUTPUT_DIR / f"{grade.replace(' ', '_')}.mp3"
            grade_audio.export(out_file, format="mp3", bitrate="128k")
            print(f"Creado: {out_file.name} — {sum(len(item.get('words', [])) for item in (main_list, final_list) if item)} palabras")
            master += grade_audio + AudioSegment.silent(duration=GRADE_PAUSE_MS)

    master_file = ROOT / "spelling-bee-todos-los-grados.mp3"
    master.export(master_file, format="mp3", bitrate="128k")
    print("\n¡Listo!")
    print(f"Palabras incorporadas (incluye repeticiones entre listas): {total_done}/{total_occurrences}")
    print(f"Audios por grado: {OUTPUT_DIR}")
    print(f"Audio maestro: {master_file}")

if __name__ == "__main__":
    main()
