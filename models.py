from enum import Enum
from typing import Union
from datetime import date
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


class StandardResponse(BaseModel):
    kode: int
    message: str
    status: bool
    value: Union[list, dict, None] = None


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


class Peminjaman(Base):
    namaPeminjam: str
    buku: Union[BukuApp, dict]
    tanggalPinjam: Union[date, str]
    statusPeminjaman: Union[StatusPeminjaman, str]


class PeminjamanDB(Peminjaman):
    key: Union[str, None] = None


class PeminjamanApp(BaseModel):
    idPeminjaman: Union[str, None] = None
    namaPeminjam: str
    buku: BukuApp
    tanggalPinjam: Union[date, str]
    statusPeminjaman: Union[str, StatusPeminjaman]


class PeminjamanPost(BaseModel):
    namaPeminjam: str
    idBuku: str




