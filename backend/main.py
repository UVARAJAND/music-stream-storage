from fastapi import FastAPI, UploadFile, File, HTTPException, Request
import requests
import base64
import os
from dotenv import load_dotenv
import uvicorn
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI(title="Music Upload API")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
USERNAME = os.getenv("GITHUB_USERNAME")
REPO = os.getenv("GITHUB_REPO")
BRANCH = os.getenv("GITHUB_BRANCH")
SONGS_PATH = os.getenv("GITHUB_SONGS_PATH")

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later restrict to your domain
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

@app.get("/songs")
def list_songs():
    url = f"https://api.github.com/repos/{USERNAME}/{REPO}/contents/{SONGS_PATH}"

    r = requests.get(url, headers=HEADERS)
    if r.status_code != 200:
        raise HTTPException(status_code=500, detail="Unable to fetch songs")

    files = [
        {
            "name": f["name"],
            "download_url": f["download_url"],
            "size": f["size"]
        }
        for f in r.json() if f["type"] == "file"
    ]

    return {"songs": files}
@app.post("/upload")
async def upload_song(file: UploadFile = File(...)):
    content = await file.read()
    encoded = base64.b64encode(content).decode("utf-8")

    url = f"https://api.github.com/repos/{USERNAME}/{REPO}/contents/{SONGS_PATH}/{file.filename}"

    payload = {
        "message": f"Upload {file.filename}",
        "content": encoded,
        "branch": BRANCH
    }

    r = requests.put(url, headers=HEADERS, json=payload)

    if r.status_code not in [200, 201]:
        raise HTTPException(status_code=500, detail=r.json())

    return {
        "message": "File uploaded successfully",
        "file": file.filename
    }
@app.delete("/delete/{filename}")
def delete_song(filename: str):
    file_url = f"https://api.github.com/repos/{USERNAME}/{REPO}/contents/{SONGS_PATH}/{filename}"

    # Get file SHA
    r = requests.get(file_url, headers=HEADERS)
    if r.status_code != 200:
        raise HTTPException(status_code=404, detail="File not found")

    sha = r.json()["sha"]

    payload = {
        "message": f"Delete {filename}",
        "sha": sha,
        "branch": BRANCH
    }

    delete_req = requests.delete(file_url, headers=HEADERS, json=payload)

    if delete_req.status_code != 200:
        raise HTTPException(status_code=500, detail="Delete failed")

    return {"message": "File deleted successfully", "file": filename}


@app.get("/stream/{filename}")
def stream_song(filename: str, request: Request):
    github_raw_url = (
        f"https://raw.githubusercontent.com/"
        f"{USERNAME}/{REPO}/{BRANCH}/{SONGS_PATH}/{filename}"
    )

    headers = {}
    range_header = request.headers.get("range")
    if range_header:
        headers["Range"] = range_header

    r = requests.get(github_raw_url, headers=headers, stream=True)

    if r.status_code not in (200, 206):
        raise HTTPException(status_code=404, detail="File not found")

    response_headers = {
        "Content-Type": r.headers.get("Content-Type", "audio/mpeg"),
        "Accept-Ranges": "bytes",
        "Cache-Control": "public, max-age=31536000, immutable",
        "Content-Range": r.headers.get("Content-Range", ""),
    }

    return StreamingResponse(
        r.iter_content(chunk_size=1024 * 256),
        status_code=r.status_code,
        headers=response_headers,
    )

if __name__ == "__main__":

    uvicorn.run("main:app", host="0.0.0.0", port=8000)

