from typing import Union
from datetime import date
from enum import Enum
from pydantic import BaseModel


class StatusBuku(Enum):
    dipinjam = "dipinjam"
    disimpan = "disimpan"
    hilang = "hilang"


class StatusPeminjaman(Enum):
    berlangsung = "berlangsung"
    selesai = "selesai"


class Base(BaseModel):
    created_at: Union[date, str] = None
    updated_at: Union[date, str] = None
    deleted_at: Union[date, str] = None


class Buku(Base):
    judulBuku: str
    jumlahHalaman: int
    penulis: str
    penerbit: str
    tahunTerbit: int
    status: Union[str, StatusBuku, None] = None


class BukuDB(Buku):
    key: Union[str, None] = None


class BukuApp(BaseModel):
    idBuku: Union[str, None] = None
    judulBuku: str
    jumlahHalaman: int
    penulis: str
    penerbit: str
    tahunTerbit: int
    status: Union[str, StatusBuku]


class BukuPost(BaseModel):
    judulBuku: str
    jumlahHalaman: int
    penulis: str
    penerbit: str
    tahunTerbit: int


class PeminjamanDB(Base):
    idPeminjaman: str
    namaPeminjam: str
    buku: Buku
    tanggalPinjam: date
    statusPeminjaman: StatusPeminjaman


class Peminjaman(BaseModel):
    idPeminjaman: str
    namaPeminjam: str
    buku: Buku
    tanggalPinjam: date
    statusPeminjaman: StatusPeminjaman


class StandardResponse(BaseModel):
    kode: int
    message: str
    status: bool
    value: Union[list, dict, None] = None

