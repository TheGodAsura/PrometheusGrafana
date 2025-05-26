
from fastapi import FastAPI, Request
from prometheus_client import Counter, Summary, generate_latest
from fastapi.responses import JSONResponse, PlainTextResponse
import time

app = FastAPI()

REQUEST_COUNT = Counter('request_count', 'Total de requisições', ['method', 'endpoint'])
REQUEST_LATENCY = Summary('request_latency_seconds', 'Tempo de resposta por rota', ['endpoint'])
ERROR_COUNT = Counter('error_count', 'Contador de erros', ['endpoint'])

books = [{"id": 1, "title": "Livro Exemplo"}]

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    method = request.method
    endpoint = request.url.path
    try:
        response = await call_next(request)
        if response.status_code >= 400:
            ERROR_COUNT.labels(endpoint=endpoint).inc()
    except Exception:
        ERROR_COUNT.labels(endpoint=endpoint).inc()
        raise
    finally:
        duration = time.time() - start_time
        REQUEST_LATENCY.labels(endpoint=endpoint).observe(duration)
        REQUEST_COUNT.labels(method=method, endpoint=endpoint).inc()
    return response

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/books")
async def get_books():
    return books

@app.post("/books")
async def add_book():
    new_book = {"id": len(books) + 1, "title": f"Livro {len(books) + 1}"}
    books.append(new_book)
    return new_book

@app.get("/metrics")
async def metrics():
    return PlainTextResponse(generate_latest().decode())
