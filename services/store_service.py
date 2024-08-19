from database import get_store_collection

async def get_nearby_stores(longitude: float, latitude: float, max_distance: int):
    store_collection = await get_store_collection()
    pipeline = [
        {
            "$geoNear": {
                "near": {"type": "Point", "coordinates": [longitude, latitude]},
                "distanceField": "distance",
                "maxDistance": max_distance,
                "spherical": True
            }
        }
    ]
    cursor = store_collection.aggregate(pipeline)
    stores = await cursor.to_list(length=None)
    return stores


async def get_all_stores():
    store_collection = await get_store_collection()
    return await store_collection.find({}).to_list(length=None)


async def update_store_location(store_code: str, longitude: float, latitude: float, store_collection):
    return await store_collection.update_one(
        {"store_code": store_code},
        {"$set": {
            "loc.coordinates": [longitude, latitude]
        }}
    )
