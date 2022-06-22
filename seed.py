from datetime import datetime
from db import db_buku
from models import BukuDB


data = []
for x in range(1, 6):
    data.append({
        "created_at": datetime.now().strftime("%d/%m/%Y"),
        "updated_at": None,
        "deleted_at": None,
        "key": f"Bu120SaSa2003{str(x).zfill(2)}",
        "judulBuku": f"Buku Baru {x}",
        "jumlahHalaman": 120,
        "penulis": "Saya",
        "penerbit": "Saya Juga",
        "tahunTerbit": 2003,
        "status": "disimpan"
    })


for x in data:
    db_buku.put(BukuDB(**x).dict())

