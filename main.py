from fastapi import FastAPI

import buku
import peminjaman

app = FastAPI(
    title="API Perpustakaan",
    version="Beta"
)

app.include_router(buku.router, prefix="/buku", tags=['Buku'])
app.include_router(peminjaman.router, prefix="/peminjaman", tags=['Peminjaman'])
