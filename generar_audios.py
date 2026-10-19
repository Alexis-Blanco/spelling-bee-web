"""Genera un MP3 por palabra única del respaldo de Spelling Bee.
Voz predeterminada: Microsoft Edge TTS en-US-AriaNeural (femenina, inglés estadounidense).
Requiere conexión a internet durante la generación.
"""
import asyncio
import json
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "audio_manifest.json"
AUDIO_DIR = ROOT / "audio"
VOICE = "en-US-AriaNeural"
CONCURRENCY = 3
RETRIES = 3

async def generate_one(semaphore, word, filename, position, total):
    target = AUDIO_DIR / filename
    if target.exists() and target.stat().st_size > 1000:
        print(f"[{position}/{total}] Ya existe: {word}")
        return True
    async with semaphore:
        for attempt in range(1, RETRIES + 1):
            try:
                communicate = edge_tts.Communicate(word, VOICE)
                await communicate.save(str(target))
                if target.exists() and target.stat().st_size > 1000:
                    print(f"[{position}/{total}] OK: {word}")
                    return True
                raise RuntimeError("El archivo generado está vacío o incompleto")
            except Exception as exc:
                if attempt == RETRIES:
                    print(f"[{position}/{total}] ERROR: {word} — {exc}")
                    try:
                        target.unlink(missing_ok=True)
                    except Exception:
                        pass
                    return False
                await asyncio.sleep(attempt * 2)

async def main():
    AUDIO_DIR.mkdir(exist_ok=True)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entries = list(manifest.items())
    semaphore = asyncio.Semaphore(CONCURRENCY)
    print(f"Voz: {VOICE}")
    print(f"Palabras únicas: {len(entries)}")
    print("No cierres esta ventana mientras se generan los archivos.\n")
    results = await asyncio.gather(*[
        generate_one(semaphore, item[1]["word"], item[1]["file"], i, len(entries))
        for i, item in enumerate(entries, 1)
    ])
    ok = sum(results)
    print(f"\nTerminado: {ok}/{len(entries)} audios generados o ya existentes.")
    failed = []
    for key, item in entries:
        target = AUDIO_DIR / item["file"]
        if not target.exists() or target.stat().st_size <= 1000:
            failed.append(item["word"])
    if failed:
        print("\nPalabras que todavía necesitan audio:")
        for word in failed:
            print(f"  - {word}")
        print("\nVuelve a ejecutar el mismo comando para reintentar solo los que faltan.")
    else:
        print("Todos los audios están listos en la carpeta audio.")

if __name__ == "__main__":
    asyncio.run(main())
