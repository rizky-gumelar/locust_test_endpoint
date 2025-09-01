from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import asyncio

app = FastAPI()

# ===== 1. Schema request =====
class LokasiInput(BaseModel):
    nopol: str
    lat: float
    long: float

# ===== 2. Simulasi ambil data dari Odoo =====
async def get_kendaraan_from_odoo(nopol: str):
    await asyncio.sleep(0.1)
    # Simulasi: anggap data ada
    return {
        "nopol": nopol,
        "driver": "Andi Saputra",
        "vehicle_type": "Truk Box",
        "fleet_id": 789
    }

# ===== 3. Simulasi reverse geocode =====
async def reverse_geocode(lat: float, long: float):
    await asyncio.sleep(0.3)
    # Simulasi: berdasarkan lat long
    return {
        "alamat": "Jl. Sudirman No. 10, Jakarta Selatan",
        "kota": "Jakarta Selatan",
        "provinsi": "DKI Jakarta",
        "kode_wilayah": "DKI-JKT-SL"
    }

async def save_location_to_odoo(vehicle_id: int, lat: float, lon: float, location_info: dict):
    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
    models.execute_kw(
        db, uid, password,
        'fleet.vehicle.location', 'create',
        [{
            'vehicle_id': vehicle_id,
            'latitude': lat,
            'longitude': lon,
            'location_text': location_info.get('alamat'),
            'region_code': location_info.get('kodepos'),
        }]
    )

# EnDPOINT
@app.post("/update-lokasi")
async def update_lokasi(data: LokasiInput):
    
    kendaraan = await get_kendaraan_from_odoo(data.nopol)
    # if not kendaraan:
    #     raise HTTPException(status_code=404, detail="Kendaraan tidak ditemukan di Odoo")

    lokasi = await reverse_geocode(data.lat, data.long)

    # await asyncio.sleep(0.2)
    # await save_location_to_odoo(kendaraan['id'], data.lat, data.long, location_info)

    # Gabungkan semua hasil
    hasil = {
        "nopol": kendaraan["nopol"],
        "driver": kendaraan["driver"],
        "vehicle_type": kendaraan["vehicle_type"],
        "fleet_id": kendaraan["fleet_id"],
        "lokasi": lokasi["alamat"],
        "kota": lokasi["kota"],
        "provinsi": lokasi["provinsi"],
        "kode_wilayah": lokasi["kode_wilayah"],
        "koordinat": {"lat": data.lat, "long": data.long},
        "timestamp": datetime.now().isoformat()
    }

    return {"status": "sukses", "data": hasil}


# async def get_vehicle_from_odoo(nopol: str):
#     models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
#     vehicle = models.execute_kw(
#         db, uid, password,
#         'fleet.vehicle', 'search_read',
#         [[['license_plate', '=', nopol]]],
#         {'fields': ['id', 'license_plate'], 'limit': 1}
#     )
#     return vehicle[0] if vehicle else None

# async def reverse_geocode(lat, lon):
#     # Contoh menggunakan Nominatim
#     async with aiohttp.ClientSession() as session:
#         async with session.get(
#             f"https://nominatim.openstreetmap.org/reverse",
#             params={
#                 "lat": lat,
#                 "lon": lon,
#                 "format": "json"
#             },
#             headers={"User-Agent": "your-app"}
#         ) as resp:
#             data = await resp.json()
#             return {
#                 "alamat": data.get("display_name"),
#                 "kota": data.get("address", {}).get("city", ""),
#                 "provinsi": data.get("address", {}).get("state", ""),
#                 "kodepos": data.get("address", {}).get("postcode", "")
#             }

# async def save_location_to_odoo(vehicle_id: int, lat: float, lon: float, location_info: dict):
#     models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
#     models.execute_kw(
#         db, uid, password,
#         'fleet.vehicle.location', 'create',
#         [{
#             'vehicle_id': vehicle_id,
#             'latitude': lat,
#             'longitude': lon,
#             'location_text': location_info.get('alamat'),
#             'region_code': location_info.get('kodepos'),
#         }]
#     )

# # EnDPOINT
# @app.post("/update-lokasi")
# async def update_lokasi(data: LokasiInput):
    
#     kendaraan = await get_kendaraan_from_odoo(data.nopol)
#     # if not kendaraan:
#     #     raise HTTPException(status_code=404, detail="Kendaraan tidak ditemukan di Odoo")

#     lokasi = await reverse_geocode(data.lat, data.long)

#     # await asyncio.sleep(0.2)
#     # await save_location_to_odoo(kendaraan['id'], data.lat, data.long, location_info)

#     # Gabungkan semua hasil
#     hasil = {
#         "nopol": kendaraan["nopol"],
#         "driver": kendaraan["driver"],
#         "vehicle_type": kendaraan["vehicle_type"],
#         "fleet_id": kendaraan["fleet_id"],
#         "lokasi": lokasi["alamat"],
#         "kota": lokasi["kota"],
#         "provinsi": lokasi["provinsi"],
#         "kode_wilayah": lokasi["kode_wilayah"],
#         "koordinat": {"lat": data.lat, "long": data.long},
#         "timestamp": datetime.now().isoformat()
#     }

#     return {"status": "sukses", "data": hasil}