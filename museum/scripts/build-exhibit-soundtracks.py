"""Fetch official CC-BY library originals and encode museum background audio.

Requires Python, imageio-ffmpeg and mutagen. Run from this Site checkout:
  python scripts/build-exhibit-soundtracks.py --cache <outside-site-cache>
Original compositions are unchanged apart from MP3 delivery transcoding.
"""

import argparse
import concurrent.futures
import hashlib
import html
import json
from pathlib import Path
import re
import subprocess
import urllib.request

import imageio_ffmpeg
from mutagen.mp3 import MP3

ROOT = Path(__file__).resolve().parents[1]
LIBRARY = "https://www.scottbuckley.com.au/library/"
LICENSE = "https://creativecommons.org/licenses/by/4.0/"
BITRATES_KBPS = {}
RETRIEVAL_DATES = {"solace": "2026-10-23"}
TRACKS = [
    ("potential", "Call To Adventure", "call-to-adventure", "2023/01/CallToAdventure.mp3"),
    ("bhsm-lifecycle", "Helios", "helios", "2020/05/sb_helios.mp3"),
    ("berger-hopf", "Time and Space", "time-and-space", "2018/02/sb_timeandspace.mp3"),
    ("science-unification", "Pathfinder", "pathfinder", "2021/04/sb_pathfinder.mp3"),
    ("science-predictions", "Discovery", "discovery", "2020/01/sb_discovery.mp3"),
    ("science-magnetic", "Artemis", "artemis", "2022/09/Artemis.mp3"),
    ("science-decays", "Race The Sun", "race-the-sun", "2022/04/sb_racethesun.mp3"),
    ("blackhole-tracker", "Solace", "solace", "2020/05/sb_solace.mp3"),
    ("cosmology-original", "Celestial", "celestial", "2021/06/sb_celestial.mp3"),
    ("other-work", "Starfire", "starfire", "2026/01/Starfire.mp3"),
    ("science-test", "Horizons", "horizons", "2020/02/sb_horizons.mp3"),
    ("research-exhibit", "Into The Unknown", "into-the-unknown", "2022/06/IntoTheUnknown.mp3"),
    ("details", "Beyond These Walls", "beyond-these-walls", "2021/05/sb_beyondthesewalls.mp3"),
    ("creator", "Ascension", "ascension", "2019/02/sb_ascension.mp3"),
    ("big-questions", "Age of Wonder", "age-of-wonder", "2022/03/AgeOfWonder.mp3"),
    ("museum-exit", "Aphelion", "aphelion", "2026/04/Aphelion.mp3"),
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def materialize(row, cache):
    slide, title, slug, remote = row
    bitrate = BITRATES_KBPS.get(slug, 160)
    source_url = LIBRARY + "wp-content/uploads/" + remote
    original = cache / remote.rsplit("/", 1)[-1]
    if not original.exists():
        request = urllib.request.Request(source_url, headers={"User-Agent": "BHSM-Museum/1.0"})
        with urllib.request.urlopen(request, timeout=120) as response:
            if response.headers.get_content_type() != "audio/mpeg":
                raise ValueError(f"Unexpected audio type: {source_url}")
            original.write_bytes(response.read())
    original_info = MP3(original).info
    output = ROOT / "public" / "audio" / f"scott-buckley-{slug}.mp3"
    subprocess.run([
        imageio_ffmpeg.get_ffmpeg_exe(), "-nostdin", "-hide_banner", "-loglevel", "error",
        "-y", "-i", str(original), "-map", "0:a:0", "-map_metadata", "-1",
        "-codec:a", "libmp3lame", "-b:a", f"{bitrate}k", "-ar", "44100", "-ac", "2",
        "-metadata", f"title={title}", "-metadata", "artist=Scott Buckley",
        "-metadata", f"copyright=Scott Buckley; CC BY 4.0; {LIBRARY}{slug}/",
        str(output),
    ], check=True)
    info = MP3(output).info
    if abs(original_info.length - info.length) > 0.2:
        raise ValueError(f"Transcoded duration mismatch: {title}")
    if output.stat().st_size > 10 * 1024 * 1024:
        raise ValueError(f"Repository asset size exceeded: {title}")
    result = {
        "slideId": slide, "title": title, "artist": "Scott Buckley",
        "source": f"./audio/{output.name}", "creditUrl": LIBRARY + slug + "/",
        "licenseUrl": LICENSE, "license": "CC BY 4.0",
        "originalUrl": source_url, "retrievedOn": RETRIEVAL_DATES.get(slug, "2026-10-22"),
        "changes": f"Transcoded to {bitrate} kbps stereo MP3 at 44.1 kHz; composition unedited.",
        "durationSeconds": round(info.length, 3), "bytes": output.stat().st_size,
        "sha256": digest(output), "originalSha256": digest(original),
    }
    print(f"Ready: {title} ({info.length:.0f}s, {output.stat().st_size:,} bytes)", flush=True)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache", type=Path, required=True)
    args = parser.parse_args()
    cache = args.cache.resolve()
    if cache.is_relative_to(ROOT):
        raise ValueError("Keep downloaded originals outside the Site archive.")
    cache.mkdir(parents=True, exist_ok=True)
    (ROOT / "public" / "audio").mkdir(parents=True, exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        tracks = list(pool.map(lambda row: materialize(row, cache), TRACKS))
    payload = json.dumps(tracks, ensure_ascii=False, indent=2) + "\n"
    (ROOT / "public" / "audio" / "exhibit-soundtracks.json").write_text(payload, encoding="utf-8")
    (ROOT / "lib" / "exhibit-soundtracks.mjs").write_text(
        "// Official library tracks; regenerated by scripts/build-exhibit-soundtracks.py.\n"
        + "export const exhibitSoundtracks = " + payload.rstrip() + ";\n", encoding="utf-8")
    write_credits(tracks)


def write_credits(tracks):
    slides = dict(re.findall(r"\['([^']+)', '([^']+)'\]", (ROOT / "lib" / "museum-slides.mjs").read_text(encoding="utf-8")))
    rows = "\n".join(
        f'<tr><td>{index:02d} · {html.escape(slides[track["slideId"]])}</td>'
        f'<td><a href="{track["creditUrl"]}">{html.escape(track["title"])}</a></td>'
        f'<td>Scott Buckley</td><td><a href="{LICENSE}">CC BY 4.0</a></td></tr>'
        for index, track in enumerate(tracks, 1)
    )
    document = '''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Music credits · BHSM Museum</title>
<style>
body{margin:0;background:#07141d;color:#eaf0ee;font:16px/1.6 system-ui,sans-serif}
main{max-width:1050px;margin:auto;padding:clamp(24px,5vw,64px)}
a{color:#9ae1ce;text-underline-offset:4px}h1{font-size:clamp(30px,5vw,48px);line-height:1.15}
p{max-width:76ch;color:#c5d2d6}.table{overflow:auto}table{width:100%;border-collapse:collapse;text-align:left}
th,td{padding:14px 12px;border-bottom:1px solid #28404b}th{color:#f6d29a}small{color:#a4b6bd}
</style><main><a href="./">← Return to the museum</a>
<h1>A soundtrack for discovery</h1>
<p>Each museum exhibit has its own instrumental theme. These original compositions are by
<a href="https://www.scottbuckley.com.au/">Scott Buckley</a> and are used under
<a href="https://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International</a>.
The tracks were transcoded to 160 kbps stereo MP3 at 44.1 kHz for background playback;
the compositions have not been edited. No endorsement by the composer is implied.</p>
<div class="table"><table><thead><tr><th scope="col">Exhibit</th><th scope="col">Composition / source</th><th scope="col">Composer</th><th scope="col">License</th></tr></thead><tbody>
''' + rows + '''
</tbody></table></div>
<p>The music accompanies an exploration of geometry, matter and the cosmos. Pause and mute controls remain available as you move between exhibits.</p>
<h2>The original museum themes</h2>
<p><a href="https://pixabay.com/music/main-title-inspiring-epic-164829/">Inspiring Epic</a> and
<a href="https://pixabay.com/music/main-title-epic-cinematic-victory-155790/">Epic Cinematic Victory</a>
by <a href="https://pixabay.com/users/paulyudin-30043746/">PaulYudin</a> were the museum's original soundtrack.
Their retained assets are used under the <a href="https://pixabay.com/service/license-summary/">Pixabay Content License</a>.</p>
<small>Source records verified 22–23 October 2026. <a href="https://www.scottbuckley.com.au/library/using-this-music/">Composer's music usage terms</a>.</small>
</main></html>
'''
    (ROOT / "public" / "soundtrack-credits.html").write_text(document, encoding="utf-8")


if __name__ == "__main__":
    main()
