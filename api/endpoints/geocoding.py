from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
import httpx
from dotenv import load_dotenv
import os
from urllib.parse import quote
from database import get_store_collection
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId

load_dotenv()

router = APIRouter()

KAKAO_API_KEY = os.getenv("KAKAO_API_KEY")


async def get_coordinates(address: str):
    url = f"https://dapi.kakao.com/v2/local/search/address.json?query={quote(address)}"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch data from Kakao API")

    data = response.json()
    if not data['documents']:
        raise HTTPException(status_code=404, detail="No results found for the given address")

    result = data['documents'][0]
    return {
        "latitude": float(result['y']),
        "longitude": float(result['x'])
    }


async def update_store_coordinates(store_collection: AsyncIOMotorCollection, store_id: ObjectId, new_coordinates: dict):
    result = await store_collection.update_one(
        {"_id": store_id},
        {"$set": {"loc": {"type": "Point", "coordinates": [new_coordinates["longitude"], new_coordinates["latitude"]]}}}
    )
    return result.modified_count > 0


@router.post("/geocode")
async def geocode_address(address: str):
    coordinates = await get_coordinates(address)
    return JSONResponse(content={
        "address": address,
        "latitude": coordinates["latitude"],
        "longitude": coordinates["longitude"]
    })


@router.get("/coordinates")
async def get_coordinates_for_address(address: str):
    coordinates = await get_coordinates(address)
    return JSONResponse(content=coordinates)


@router.get("/store_coordinates")
async def get_coordinates_for_store(
        store_name: str,
        update_db: bool = Query(False, description="Whether to update the database if coordinates differ"),
        store_collection: AsyncIOMotorCollection = Depends(get_store_collection)
):
    # 상점명으로 DB에서 정보 찾기
    store = await store_collection.find_one({"name": store_name})
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    db_coordinates = None
    if "loc" in store and "coordinates" in store["loc"]:
        db_coordinates = {
            "longitude": store["loc"]["coordinates"][0],
            "latitude": store["loc"]["coordinates"][1]
        }

    # 주소로 좌표 찾기
    api_coordinates = await get_coordinates(store["addr"])

    coordinates_match = db_coordinates and \
                        abs(db_coordinates["latitude"] - api_coordinates["latitude"]) < 1e-6 and \
                        abs(db_coordinates["longitude"] - api_coordinates["longitude"]) < 1e-6

    if not coordinates_match and update_db:
        updated = await update_store_coordinates(store_collection, store["_id"], api_coordinates)
        if updated:
            db_coordinates = api_coordinates

    return JSONResponse(content={
        "store_name": store_name,
        "address": store["addr"],
        "latitude": api_coordinates["latitude"],
        "longitude": api_coordinates["longitude"],
        "db_coordinates": db_coordinates,
        "coordinates_updated": not coordinates_match and update_db
    })

