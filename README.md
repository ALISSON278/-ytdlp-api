# YouTube Downloader API

API simples para obter links diretos de vídeos do YouTube usando yt-dlp.

## Endpoints

### GET /
Verifica se a API está online.

### POST /download
Obtém o link direto do vídeo.

**Body:**
```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

**Response:**
```json
{
  "success": true,
  "video_url": "https://...",
  "title": "Título do vídeo",
  "duration": 120
}
```

### POST /info
Obtém informações do vídeo sem baixar.

**Body:**
```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

## Deploy no Railway

1. Crie um repositório no GitHub com estes arquivos
2. No Railway, clique em "New Project"
3. Selecione "Deploy from GitHub repo"
4. Escolha o repositório
5. Railway vai fazer deploy automaticamente
6. Copie a URL gerada (ex: https://seu-app.railway.app)
