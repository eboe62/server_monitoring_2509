import os
import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse

app = FastAPI(title="Claude Code Governance Proxy")

# La API Key real de Anthropic se la pasaremos de forma segura al proxy
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_request(path: str, request: Request):
    # 1. Auditoría interna (Ver qué está haciendo Claude)
    body = await request.body()
    print(f"--- [AUDITORÍA] Petición entrante a: /{path} ---")
    if body:
        # Imprime los prompts en los logs de Docker (puedes guardarlo en BD o archivo si quieres)
        print(body.decode("utf-8", errors="ignore")[:1000]) # Muestra los primeros 1000 caracteres

    # 2. Reenviar a Anthropic
    url = f"https://api.anthropic.com/{path}"
    headers = dict(request.headers)

    # Inyectamos la API Key real y forzamos el Host correcto para Anthropic
    headers["host"] = "api.anthropic.com"
    if ANTHROPIC_API_KEY:
        headers["x-api-key"] = ANTHROPIC_API_KEY

    async def stream_response():
        async with httpx.AsyncClient() as client:
            # Reenviamos exactamente los mismos headers y body
            async with client.stream(
                request.method, url, headers=headers, content=body, timeout=60.0
            ) as response:
                async for chunk in response.aiter_bytes():
                    yield chunk

    return StreamingResponse(stream_response(), media_type="application/json")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
