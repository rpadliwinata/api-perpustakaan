import unittest
from unittest import IsolatedAsyncioTestCase
from buku import ambil_data_buku, StandardResponse


class TestBukuAPI(IsolatedAsyncioTestCase):
    async def test_response_value(self):
        res = await ambil_data_buku()
        self.assertEqual(type(res.value), list)

    async def test_response_type(self):
        res = await ambil_data_buku()
        self.assertEqual(type(res), StandardResponse)


if __name__ == "__main__":
    unittest.main()
