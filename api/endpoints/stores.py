from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from services.store_service import get_nearby_stores, get_all_stores
from utils.json_encoder import parse_json

router = APIRouter()

@router.get("/nearby")
async def get_nearby_stores_endpoint(
    longitude: float = Query(...),
    latitude: float = Query(...),
    max_distance: int = Query(2000, ge=0, le=5000)
):
    stores = await get_nearby_stores(longitude, latitude, max_distance)
    return JSONResponse(content=parse_json(stores))

@router.get("/all")
async def get_all_stores_endpoint():
    stores = await get_all_stores()
    return JSONResponse(content=parse_json(stores))


