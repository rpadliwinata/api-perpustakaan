from types import SimpleNamespace
from datetime import datetime

from fastapi import APIRouter, status
from deta.base import FetchResponse

from models import *
from buku import get_for_app
from db import db_peminjaman as db
from db import db_buku

router = APIRouter()


def get_latest_digit(id_peminjaman: str, result: FetchResponse) -> str:
    data = [SimpleNamespace(**x) for x in result.items]
    keys = [x.key for x in data]
    keys = [x for x in keys if id_peminjaman in x]
    if len(keys) != 0:
        digit = [int(x[-2:]) for x in keys]
        return str(max(digit) + 1).zfill(2)
    else:
        return "-"


@router.get("/get", response_model=StandardResponse)
async def ambil_data_buku(idPeminjaman: Union[str, None] = None):
    if idPeminjaman:
        res = db.get(idPeminjaman)
        if not res or res['deleted_at'] is not None:
            return StandardResponse(kode=status.HTTP_404_NOT_FOUND,
                                    message="Data tidak ditemukan",
                                    status=False)
        res['idPeminjaman'] = res['key']
        pinjam = PeminjamanApp(**res)
        data = pinjam.dict()
        data['judulBuku'] = data['buku']['judulBuku']
        pinjam = PeminjamanDashboard(**data)
    else:
        res = db.fetch()
        for x in res.items:
            x['idPeminjaman'] = x['key']
        pinjam = [PeminjamanApp(**x) for x in res.items if x['deleted_at'] is None]
        data = [x.dict() for x in pinjam]
        for x in data:
            x['judulBuku'] = x['buku']['judulBuku']
        pinjam = [PeminjamanDashboard(**x) for x in data]
    response = StandardResponse(kode=status.HTTP_200_OK,
                                message="Data berhasil diambil",
                                status=True,
                                value=pinjam)
    return response


@router.post("/post", response_model=StandardResponse)
async def simpan_data_peminjaman(pinjam: PeminjamanPost):
    id_buku = pinjam.idBuku
    buku = get_for_app(pinjam.idBuku, db_buku, BukuApp)
    buku.status = StatusBuku.dipinjam.value
    buku.idBuku = id_buku
    db_buku.update(buku.dict(), id_buku)
    data = pinjam.dict()
    data['created_at'] = datetime.now().strftime("%d/%m/%Y")
    data['tanggalPinjam'] = datetime.now().strftime("%d/%m/%Y")
    data['statusPeminjaman'] = StatusPeminjaman.berlangsung
    data['buku'] = buku.dict()
    pinjam = PeminjamanDB(**data)
    pinjam.statusPeminjaman = pinjam.statusPeminjaman.value
    key = f"{pinjam.namaPeminjam[:3]}{id_buku[:3]}{datetime.today().day}"
    digit = get_latest_digit(key, db.fetch())
    if digit != "-":
        pinjam.key = key + digit
    else:
        pinjam.key = key + "01"
    res = db.insert(pinjam.dict())
    res['idPeminjaman'] = res['key']
    res['idBuku'] = res['buku']['idBuku']
    response = StandardResponse(kode=status.HTTP_200_OK,
                                message="Peminjaman berhasil dibuat",
                                status=True,
                                value=PeminjamanID(**res))
    return response


@router.patch("/patch", response_model=StandardResponse)
async def update_data_peminjaman(pinjam: PeminjamanApp):
    key = pinjam.idPeminjaman
    pinjam = Peminjaman(**pinjam.dict())
    pinjam.statusPeminjaman = pinjam.statusPeminjaman.value
    pinjam.updated_at = datetime.now().strftime("%d/%m/%Y")
    db.update(pinjam.dict(), key)
    try:
        db.update(pinjam.dict(), key)
    except:
        return StandardResponse(kode=status.HTTP_400_BAD_REQUEST,
                                message="Gagal update data buku",
                                status=False)
    return StandardResponse(kode=status.HTTP_200_OK,
                            message="Berhasil update data peminjaman",
                            status=True,
                            value=PeminjamanApp(**pinjam.dict()))


@router.delete("/delete", response_model=StandardResponse)
async def hapus_data_peminjaman(idPeminjaman: str):
    pinjam = Peminjaman(**db.get(idPeminjaman))
    pinjam.deleted_at = datetime.today().strftime("%d/%m/%Y")
    try:
        db.update(pinjam.dict(), idPeminjaman)
    except:
        return StandardResponse(kode=status.HTTP_404_NOT_FOUND,
                                message="Gagal menghapus peminjaman",
                                status=False)
    return StandardResponse(kode=status.HTTP_200_OK,
                            message="Berhasil menghapus peminjaman",
                            status=True,
                            value=pinjam.dict())


@router.get("/kembalikan/{id_buku}", response_model=StandardResponse)
async def kembalikan_buku(id_buku):
    buku = Buku(**db_buku.get(id_buku))
    buku.updated_at = datetime.now().strftime("%d/%m/%Y")
    buku.status = StatusBuku.disimpan.value
    db_buku.update(buku.dict(), id_buku)
    data = db.fetch({"buku.idBuku": id_buku}).items[0]
    pinjam = Peminjaman(**data)
    pinjam.statusPeminjaman = StatusPeminjaman.selesai.value
    pinjam.updated_at = datetime.now().strftime("%d/%m/%Y")
    db.update(pinjam.dict(), data['key'])
    data = pinjam.dict()
    data['judulBuku'] = data['buku']['judulBuku']
    pinjam = PeminjamanDashboard(**data)
    return StandardResponse(kode=status.HTTP_200_OK,
                            message="Buku berhasil dikembalikan",
                            status=True,
                            value=pinjam)


