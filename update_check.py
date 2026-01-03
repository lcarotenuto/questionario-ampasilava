import json
import platform
import re
import ssl
from pathlib import Path
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen

import certifi

from version import __version__  # es "1.0.0" senza v

LATEST_JSON_URL = "https://lcarotenuto.github.io/questionario-ampasilava/latest.json"

def _parse_version(v: str) -> tuple[int, int, int]:
    """
    Accetta '1.2.3' o 'v1.2.3' -> (1,2,3)
    """
    v = (v or "").strip()
    m = re.match(r"^v?(\d+)\.(\d+)\.(\d+)$", v)
    if not m:
        return (0, 0, 0)
    return tuple(map(int, m.groups()))


def _is_newer(remote_version: str, local_version: str) -> bool:
    return _parse_version(remote_version) > _parse_version(local_version)


def _fetch_latest_json() -> dict:
    req = Request(
        LATEST_JSON_URL,
        headers={
            "Accept": "application/json",
            "User-Agent": "Questionario-Updater",
            "Cache-Control": "no-cache",
        },
    )
    ctx = ssl.create_default_context(cafile=certifi.where())

    try:
        with urlopen(req, timeout=20, context=ctx) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        raise RuntimeError(f"Errore HTTP {e.code} scaricando latest.json: {LATEST_JSON_URL}") from e
    except URLError as e:
        raise RuntimeError(f"Errore di rete scaricando latest.json: {e}") from e


def _pick_download_url(latest: dict) -> tuple[str, str]:
    """
    Ritorna (remote_version, url_asset)
    """
    remote_version = latest.get("version", "").strip()
    assets = latest.get("assets", {}) or {}

    system = platform.system().lower()
    if "windows" in system:
        url = assets.get("windows")
    else:
        url = assets.get("macos")

    if not remote_version or not url:
        raise RuntimeError("latest.json non contiene version/assets validi.")

    return remote_version, url


def _download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = Request(url, headers={"User-Agent": "Questionario-Updater"})

    with urlopen(req, timeout=120) as resp, open(dest, "wb") as f:
        total = resp.headers.get("Content-Length")
        total = int(total) if total and total.isdigit() else None
        read = 0

        while True:
            chunk = resp.read(1024 * 256)
            if not chunk:
                break
            f.write(chunk)
            read += len(chunk)
            if total:
                pct = int(read * 100 / total)
                print(f"\rDownload {pct}%...", end="")

    if total:
        print()
    print("Download completato:", dest)


def check_update_and_download(downloads_dir: str | None = None) -> Path | None:
    """
    - Se non c'è update: ritorna None
    - Se c'è update: scarica lo zip e ritorna Path del file
    """
    local_version = __version__  # "1.0.0"

    latest = _fetch_latest_json()
    remote_version, asset_url = _pick_download_url(latest)

    if not _is_newer(remote_version, local_version):
        print(f"Nessun aggiornamento. Locale={local_version}, Remoto={remote_version}")
        return None

    if downloads_dir is None:
        downloads_dir = str(Path.home() / "Downloads" / "Questionario_updates")

    # nome file pulito
    filename = asset_url.split("/")[-1]
    out = Path(downloads_dir) / f"v{remote_version}_{filename}"

    print(f"Aggiornamento disponibile: v{remote_version} (locale {local_version})")
    print("Scarico:", asset_url)
    _download(asset_url, out)
    return out


if __name__ == "__main__":
    p = check_update_and_download()
    if p:
        print("\nZip scaricato in:", p)
        print("Istruzioni: chiudi l'app, estrai lo zip e sostituisci i file dell'app.")
        print("Il database NON va toccato (deve restare nella cartella dati dell’utente).")