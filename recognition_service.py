import os
import time
import base64
import hmac
import hashlib
import httpx
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("ACRCLOUD_HOST", "")
ACCESS_KEY = os.getenv("ACRCLOUD_ACCESS_KEY", "")
ACCESS_SECRET = os.getenv("ACRCLOUD_ACCESS_SECRET", "")

async def recognize_audio(file_bytes: bytes) -> dict:
    """Reconnaissance via l'API HTTP d'ACRCloud (sans SDK externe)."""
    if not ACCESS_KEY or ACCESS_KEY == "votre_access_key_acrcloud":
        return {
            "status": "error",
            "message": "Clés ACRCloud manquantes dans le .env"
        }

    http_method = "POST"
    http_uri = "/v1/identify"
    data_type = "audio"
    signature_version = "1"
    timestamp = str(int(time.time()))

    string_to_sign = f"{http_method}\n{http_uri}\n{ACCESS_KEY}\n{data_type}\n{signature_version}\n{timestamp}"
    sign = base64.b64encode(
        hmac.new(
            ACCESS_SECRET.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            digestmod=hashlib.sha1
        ).digest()
    ).decode('utf-8')

    files = {'sample': file_bytes}
    data = {
        'access_key': ACCESS_KEY,
        'sample_bytes': len(file_bytes),
        'timestamp': timestamp,
        'signature': sign,
        'data_type': data_type,
        'signature_version': signature_version
    }

    req_url = f"https://{HOST}{http_uri}"

    async with httpx.AsyncClient() as client:
        res = await client.post(req_url, data=data, files=files)

    if res.status_code != 200:
        return {"status": "error", "message": f"Erreur serveur ACRCloud: {res.status_code}"}

    result = res.json()
    status_code = result.get("status", {}).get("code")

    if status_code == 0 and "metadata" in result and "music" in result["metadata"]:
        music = result["metadata"]["music"][0]
        title = music.get("title")
        artist = music["artists"][0]["name"] if music.get("artists") else "Artiste inconnu"
        album = music.get("album", {}).get("name", "")
        return {
            "status": "success",
            "title": title,
            "artist": artist,
            "album": album
        }

    return {"status": "error", "message": "Aucun morceau reconnu."}

