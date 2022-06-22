from datetime import datetime
from typing import Union, ClassVar
from types import SimpleNamespace

from fastapi import APIRouter, status
from deta.base import FetchResponse

from models import BukuDB, BukuApp, BukuPost, StatusBuku, Buku, StandardResponse, PeminjamanApp
from db import db_buku as db


router = APIRouter()


def get_for_app(id_record: str, database: db, class_: Union[type(BukuApp)]) ->\
        Union[BukuApp, PeminjamanApp]:
    res = database.get(id_record)
    if 'idBuku' in res:
        res['idBuku'] = res['key']
    objek = class_(**res)
    return objek


def get_latest_digit(id_buku: str, result: FetchResponse) -> str:
    data = [SimpleNamespace(**x) for x in result.items]
    keys = [x.key for x in data]
    keys = [x for x in keys if id_buku in x]
    if len(keys) != 0:
        digit = [int(x[-2:]) for x in keys]
        return str(max(digit) + 1).zfill(2)
    else:
        return "-"


@router.get("/get", response_model=StandardResponse)
async def ambil_data_buku(idBuku: Union[str, None] = None):
    if idBuku:
        res = db.get(idBuku)
        if not res or res['deleted_at'] is not None:
            return StandardResponse(kode=status.HTTP_404_NOT_FOUND,
                                    message="Data tidak ditemukan",
                                    status=False)
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
    buku.updated_at = datetime.now().strftime("%d/%m/%Y")
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
    buku.deleted_at = datetime.today().strftime("%d/%m/%Y")
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



