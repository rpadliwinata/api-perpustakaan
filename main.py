from fastapi import FastAPI

import models
import db
import buku


app = FastAPI(
    title="API Perpustakaan",
    version="Beta"
)

app.include_router(buku.router, prefix="/buku", tags=['Buku'])
