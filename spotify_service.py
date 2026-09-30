import os
import csv
from datetime import datetime
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

PLAYLIST_NAME = "Shazify Découvertes"
CSV_FILE = "history.csv"

def save_to_csv(title: str, artist: str, status: str):
    """Sauvegarde le morceau identifié dans history.csv."""
    file_exists = os.path.exists(CSV_FILE)
    
    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Date", "Morceau", "Artiste", "Statut"])
        
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow([now_str, title, artist, status])

def get_spotify_client():
    scope = "playlist-modify-public playlist-modify-private user-library-modify"
    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        scope=scope
    ))

def get_or_create_playlist(sp, user_id):
    playlists = sp.current_user_playlists()
    for item in playlists.get("items", []):
        if item["name"] == PLAYLIST_NAME:
            return item["id"]
    
    new_playlist = sp.user_playlist_create(user=user_id, name=PLAYLIST_NAME, public=False)
    return new_playlist["id"]

def search_and_add_track(query: str) -> dict:
    try:
        sp = get_spotify_client()
        user_id = sp.current_user()["id"]
        
        # 1. Recherche du morceau
        results = sp.search(q=query, limit=1, type="track")
        tracks = results.get("tracks", {}).get("items", [])
        
        if not tracks:
            return {"status": "error", "message": f"Morceau non trouvé sur Spotify : {query}"}
        
        track = tracks[0]
        track_uri = track["uri"]
        track_id = track["id"]
        track_name = track["name"]
        artist_name = track["artists"][0]["name"]
        
        images = track.get("album", {}).get("images", [])
        cover_url = images[0]["url"] if images else ""
        spotify_url = track.get("external_urls", {}).get("spotify", "")
        
        # 2. Récupérer ou créer la playlist
        playlist_id = get_or_create_playlist(sp, user_id)
        
        # 3. Vérifier les doublons
        playlist_tracks = sp.playlist_items(playlist_id)
        existing_uris = [item["track"]["uri"] for item in playlist_tracks.get("items", []) if item.get("track")]
        
        already_exists = track_uri in existing_uris
        status_label = "Déjà présent" if already_exists else "Ajouté"
        
        if not already_exists:
            sp.playlist_add_items(playlist_id, [track_uri])
        
        # 4. Sauvegarde automatique dans history.csv
        save_to_csv(track_name, artist_name, status_label)
        
        return {
            "status": "already_exists" if already_exists else "success",
            "message": "Morceau déjà présent" if already_exists else f"Ajouté à {PLAYLIST_NAME}",
            "track": f"{track_name} - {artist_name}",
            "track_id": track_id,
            "cover_url": cover_url,
            "spotify_url": spotify_url
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

