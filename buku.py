from datetime import datetime
from typing import Union, List
from types import SimpleNamespace

from fastapi import APIRouter, status
from deta.base import FetchResponse

from models import BukuDB, BukuApp, BukuPost, StatusBuku, Buku, StandardResponse
from db import db_buku as db


router = APIRouter()


def get_latest_digit(id_buku: str, result: FetchResponse) -> str:
    data = [SimpleNamespace(**x) for x in result.items]
    keys = [x.key for x in data]
    keys = [x for x in keys if id_buku in x]
    if len(keys) != 0:
        digit = [int(x[-2:]) for x in keys]
        return str(max(digit) + 1).zfill(2)
    else:
        return "-"


@router.get("/get", response_model=List[BukuApp])
async def ambil_data_buku(id_buku: Union[str, None] = None):
    if id_buku:
        res = db.get(id_buku)
        res['idBuku'] = res['key']
        buku = BukuApp(**res)
    else:
        res = db.fetch()
        for x in res.items:
            x['idBuku'] = x['key']
        buku = [BukuApp(**x) for x in res.items if x['deleted_at'] is None]
    response = StandardResponse(kode=status.HTTP_200_OK,
                                message="Data berhasil diambil",
                                status=True,
                                value=buku)
    return response


@router.post("/post", response_model=StandardResponse)
async def simpan_data_buku(buku: BukuPost):
    buku = BukuDB(**buku.dict())
    buku.created_at = datetime.now().strftime("%d/%m/%Y")
    buku.status = StatusBuku.disimpan.value
    key = f"{buku.judulBuku[:2]}{buku.jumlahHalaman}{buku.penulis[:3]}{buku.penerbit[:3]}{buku.tahunTerbit}"
    digit = get_latest_digit(key, db.fetch())
    if digit != "-":
        buku.key = key + digit
    else:
        buku.key = key + "01"
    res = db.insert(buku.dict())
    res['idBuku'] = res['key']
    response = StandardResponse(kode=status.HTTP_200_OK,
                                message="Buku berhasil disimpan",
                                status=True,
                                value=BukuApp(**res)).dict()
    return response


@router.patch("/patch", response_model=StandardResponse)
async def update_data_buku(buku: BukuApp):
    key = buku.idBuku
    buku = Buku(**buku.dict())
    try:
        db.update(buku.dict(), key)
    except:
        return StandardResponse(kode=status.HTTP_400_BAD_REQUEST,
                                message="Gagal update data buku",
                                status=False)
    return BukuApp(**buku.dict())


@router.delete("/delete", response_model=StandardResponse)
async def delete_data_buku(idBuku: str):
    buku = Buku(**db.get(idBuku))
    buku.deleted_at = datetime.today().date().strftime("%d/%m/%Y")
    try:
        db.update(buku.dict(), idBuku)
    except:
        return StandardResponse(kode=status.HTTP_400_BAD_REQUEST,
                                message="Gagal hapus data buku",
                                status=False)
    return StandardResponse(kode=status.HTTP_200_OK,
                            message="Data buku berhasil dihapus",
                            status=True,
                            value=buku)


# @router.post("/post", response_model=BukuApp)
# async def simpan_data_buku(buku: BukuApp):
#

