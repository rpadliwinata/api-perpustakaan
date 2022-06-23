from fastapi import FastAPI
from fastapi.responses import RedirectResponse

import buku
import peminjaman

app = FastAPI(
    title="API Perpustakaan",
    version="Beta"
)


@app.get("/", response_class=RedirectResponse, include_in_schema=False)
async def home():
    return "https://w5bzmo.deta.dev/docs"

app.include_router(buku.router, prefix="/buku", tags=['Buku'])
app.include_router(peminjaman.router, prefix="/peminjaman", tags=['Peminjaman'])
