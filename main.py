from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp
import os

app = FastAPI(title="YouTube Downloader API")

# Permitir CORS para o n8n chamar
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoRequest(BaseModel):
    url: str

class VideoResponse(BaseModel):
    success: bool
    video_url: str = None
    title: str = None
    duration: int = None
    error: str = None

@app.get("/")
def read_root():
    return {"status": "online", "service": "YouTube Downloader API"}

@app.post("/download", response_model=VideoResponse)
def download_video(request: VideoRequest):
    try:
        ydl_opts = {
            'format': 'best[ext=mp4][height<=720]/best[ext=mp4]/best',
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(request.url, download=False)
            
            # Pega a URL direta do vídeo
            video_url = info.get('url')
            
            # Se não tiver URL direta, pega dos formatos
            if not video_url and 'formats' in info:
                for fmt in reversed(info['formats']):
                    if fmt.get('url') and fmt.get('ext') == 'mp4':
                        video_url = fmt['url']
                        break
                
                # Se ainda não achou, pega qualquer formato
                if not video_url:
                    for fmt in reversed(info['formats']):
                        if fmt.get('url'):
                            video_url = fmt['url']
                            break
            
            if not video_url:
                raise HTTPException(status_code=400, detail="Não foi possível obter URL do vídeo")
            
            return VideoResponse(
                success=True,
                video_url=video_url,
                title=info.get('title', 'Sem título'),
                duration=info.get('duration', 0)
            )
            
    except Exception as e:
        return VideoResponse(
            success=False,
            error=str(e)
        )

@app.post("/info")
def get_video_info(request: VideoRequest):
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(request.url, download=False)
            
            return {
                "success": True,
                "title": info.get('title'),
                "duration": info.get('duration'),
                "thumbnail": info.get('thumbnail'),
                "description": info.get('description', '')[:500],
                "uploader": info.get('uploader')
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
