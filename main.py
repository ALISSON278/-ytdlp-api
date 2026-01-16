from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
import yt_dlp
import os
import tempfile
import base64

app = FastAPI(title="YouTube Downloader API")

# Permitir CORS
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
    video_base64: str = None
    title: str = None
    duration: int = None
    error: str = None

@app.get("/")
def read_root():
    return {"status": "online", "service": "YouTube Downloader API", "version": "2.0"}

@app.post("/download")
def download_video(request: VideoRequest):
    """Baixa o vídeo e retorna em base64"""
    try:
        # Cria pasta temporária
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = os.path.join(tmp_dir, 'video.mp4')
            
            ydl_opts = {
                'format': 'best[ext=mp4][height<=720]/best[ext=mp4]/best',
                'outtmpl': output_path,
                'quiet': True,
                'no_warnings': True,
                'socket_timeout': 30,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(request.url, download=True)
                
                # Encontra o arquivo baixado
                if os.path.exists(output_path):
                    video_file = output_path
                else:
                    # Procura por qualquer arquivo mp4 na pasta
                    for f in os.listdir(tmp_dir):
                        if f.endswith('.mp4'):
                            video_file = os.path.join(tmp_dir, f)
                            break
                    else:
                        return {"success": False, "error": "Arquivo não encontrado após download"}
                
                # Lê o arquivo e converte para base64
                with open(video_file, 'rb') as f:
                    video_bytes = f.read()
                
                video_base64 = base64.b64encode(video_bytes).decode('utf-8')
                
                return {
                    "success": True,
                    "video_base64": video_base64,
                    "title": info.get('title', 'Video'),
                    "duration": info.get('duration', 0),
                    "filesize": len(video_bytes)
                }
                
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/download-file")
def download_video_file(request: VideoRequest):
    """Baixa o vídeo e retorna como arquivo binário"""
    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = os.path.join(tmp_dir, 'video.mp4')
            
            ydl_opts = {
                'format': 'best[ext=mp4][height<=720]/best[ext=mp4]/best',
                'outtmpl': output_path,
                'quiet': True,
                'no_warnings': True,
                'socket_timeout': 30,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.extract_info(request.url, download=True)
                
                # Encontra o arquivo
                if os.path.exists(output_path):
                    video_file = output_path
                else:
                    for f in os.listdir(tmp_dir):
                        if f.endswith('.mp4'):
                            video_file = os.path.join(tmp_dir, f)
                            break
                    else:
                        raise HTTPException(status_code=500, detail="Arquivo não encontrado")
                
                with open(video_file, 'rb') as f:
                    video_bytes = f.read()
                
                return Response(
                    content=video_bytes,
                    media_type="video/mp4",
                    headers={
                        "Content-Disposition": "attachment; filename=video.mp4"
                    }
                )
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/info")
def get_video_info(request: VideoRequest):
    """Retorna apenas informações do vídeo sem baixar"""
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(request.url, download=False)
            
            return {
                "success": True,
                "title": info.get('title'),
                "duration": info.get('duration'),
                "thumbnail": info.get('thumbnail'),
                "description": info.get('description', '')[:500]
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
