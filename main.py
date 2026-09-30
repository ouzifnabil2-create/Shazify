import os
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse

from recognition_service import recognize_audio
from spotify_service import search_and_add_track

app = FastAPI(title="Shazify API")

@app.get("/", response_class=HTMLResponse)
async def get_index():
    if os.path.exists("static/index.html"):
        with open("static/index.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Shazify API en cours d exécution.</h1>"

@app.get("/api/download-history")
async def download_history():
    if os.path.exists("history.csv"):
        return FileResponse("history.csv", media_type="text/csv", filename="shazify_history.csv")
    return JSONResponse(status_code=404, content={"message": "Aucun historique disponible."})

@app.post("/api/identify-and-add")
async def identify_and_add(file: UploadFile = File(...)):
    file_bytes = await file.read()
    
    rec_result = await recognize_audio(file_bytes)
    if rec_result.get("status") != "success":
        return JSONResponse(status_code=400, content=rec_result)

    title = rec_result["title"]
    artist = rec_result["artist"]
    query = f"{title} {artist}"

    spotify_result = search_and_add_track(query)
    
    return {
        "status": spotify_result.get("status", "success"),
        "recognized": {
            "title": title,
            "artist": artist,
            "album": rec_result.get("album", "")
        },
        "spotify": spotify_result
    }

