from datetime import date, datetime
from typing import Union, List

from deta import Deta
from fastapi import FastAPI, APIRouter, status
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel

app = FastAPI(
    title="API Perpustakaan",
    version="Beta"
)

deta = Deta("c09hsnq1_68oZtotezJhC9N2jcEvUqR9nBrbdHomk")
buku = deta.Base("buku")
peminjaman = deta.Base("peminjaman")

router_buku = APIRouter()
router_peminjaman = APIRouter()


class GetBuku(BaseModel):
    idBuku: str
    judulBuku: str
    jumlahHalaman: int
    penulis: str
    penerbit: str
    tahunTerbit: int
    status: str


class PostBuku(BaseModel):
    judulBuku: str
    jumlahHalaman: int
    penulis: str
    penerbit: str
    tahunTerbit: int
    idBuku: Union[str, None] = None
    status: Union[str, None] = None


class PostPeminjaman(BaseModel):
    idPeminjaman: Union[str, None] = None
    namaPeminjam: str
    idBuku: str
    tanggalPinjam: Union[date, str, None] = None
    statusPeminjaman: Union[str, None] = None


class Buku:
    def __init__(self, *args, **kwargs):
        try:
            self.idBuku = kwargs['idBuku'] or f"{kwargs['judulBuku'][:2]}{kwargs['jumlahHalaman']}{kwargs['penulis'][:3]}{kwargs['penerbit'][:3]}" \
                                  f"{kwargs['tahunTerbit']}"
        except:
            self.idBuku = kwargs['key']

        self.judulBuku = kwargs['judulBuku']
        self.jumlahHalaman = kwargs['jumlahHalaman']
        self.penulis = kwargs['penulis']
        self.penerbit = kwargs['penerbit']
        self.tahunTerbit = kwargs['tahunTerbit']
        self.status = kwargs['status'] or "disimpan"

    def get_for_deta(self):
        return {
            "key": self.idBuku,
            "judulBuku": self.judulBuku,
            "jumlahHalaman": self.jumlahHalaman,
            "penulis": self.penulis,
            "penerbit": self.penerbit,
            "tahunTerbit": self.tahunTerbit,
            "status": self.status
        }

    def get_for_app(self):
        return {
            "idBuku": self.idBuku,
            "judulBuku": self.judulBuku,
            "jumlahHalaman": self.jumlahHalaman,
            "penulis": self.penulis,
            "penerbit": self.penerbit,
            "tahunTerbit": self.tahunTerbit,
            "status": self.status
        }


class Peminjaman:
    def __init__(self, **kwargs):
        self.tanggalPinjam = kwargs["tanggalPinjam"] or date.today()
        if type(self.tanggalPinjam) == str:
            self.tanggalPinjam = datetime.strptime(self.tanggalPinjam, "%d/%m/%Y").date()
        try:
            self.idPeminjaman = kwargs["idPeminjaman"] or f"{kwargs['namaPeminjam'][:3]}{kwargs['idBuku'][:3]}{self.tanggalPinjam.day}"
        except:
            self.idPeminjaman = kwargs["key"]
        self.namaPeminjam = kwargs['namaPeminjam']
        try:
            self.buku = Buku(**buku.get(kwargs['idBuku']))
        except:
            self.buku = Buku(**kwargs['buku'])
        self.statusPeminjaman = kwargs['statusPeminjaman']

    def get_for_deta(self):
        return {
            "key": self.idPeminjaman,
            "namaPeminjam": self.namaPeminjam,
            "buku": self.buku.get_for_app(),
            "tanggalPinjam": self.tanggalPinjam.strftime("%d/%m/%Y"),
            "statusPeminjaman": self.statusPeminjaman
        }

    def get_for_app(self):
        return {
            "idPeminjaman": self.idPeminjaman,
            "namaPeminjam": self.namaPeminjam,
            "buku": self.buku.get_for_app(),
            "tanggalPinjam": self.tanggalPinjam.strftime("%d/%m/%Y"),
            "statusPeminjaman": self.statusPeminjaman
        }


@router_buku.get("/get", response_model=Union[List[GetBuku], GetBuku])
async def get_buku(idBuku: Union[str, None] = None):
    """
    Mengambil semua data buku yang ada di database
    """
    if not idBuku:
        result = buku.fetch()
        res = [Buku(**x) for x in result.items]
        res = [x.get_for_app() for x in res]
        return res
    else:
        result = buku.get(idBuku)
        if result:
            return Buku(**result).get_for_app()
        else:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": "Buku tidak ditemukan"})


@router_buku.post("/post")
async def post_buku(book: PostBuku):
    """
    Menyimpan data ke database
    """
    book = Buku(**book.dict())
    try:
        buku.insert(book.get_for_deta())
        return JSONResponse(status_code=status.HTTP_200_OK, content={
            "kode": 200,
            "message": "Data buku berhasil disimpan",
            "status": True,
            "value": book.get_for_app()
        })
    except:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "kode": 400,
            "message": "Id Buku sudah terdaftar"
        })


@router_buku.patch("/patch")
async def put_buku(book: PostBuku):
    """
    Mengupdate data buku berdasarkan idBuku
    """
    book = Buku(**book.dict())
    buku.update(book.get_for_app(), book.idBuku)
    return book.get_for_app()


@router_buku.delete('/delete')
async def delete_buku(id_buku: str):
    """
    Menghapus data buku berdasarkan idBuku
    """
    book = buku.get(id_buku)
    buku.delete(id_buku)
    return book


@router_peminjaman.get("/get")
async def get_peminjaman(idPeminjaman: Union[str, None] = None):
    """
    Mengambil satu/semua data peminjaman yang ada di database
    """
    if not idPeminjaman:
        result = peminjaman.fetch()
        res = [Peminjaman(**x) for x in result.items]
        res = [x.get_for_app() for x in res]
    else:
        result = buku.get(idPeminjaman)
        res = Buku(**result).get_for_app()
    return res


@router_peminjaman.post("/post")
async def post_peminjaman(pinjam: PostPeminjaman):
    """
    Menyimpan data ke database
    """
    pinjam = Peminjaman(**pinjam.dict())
    res = peminjaman.put(pinjam.get_for_deta())
    return res


@router_peminjaman.patch("/patch")
async def patch_peminjaman(pinjam: PostPeminjaman):
    """
    Update data peminjaman berdasarkan key
    """



@app.get("/", response_class=RedirectResponse, include_in_schema=False)
async def home():
    return "https://w5bzmo.deta.dev/docs"

app.include_router(router_buku, prefix='/buku', tags=['Buku'])
app.include_router(router_peminjaman, prefix='/peminjaman', tags=['Peminjaman'])

