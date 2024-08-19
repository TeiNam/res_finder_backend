from motor.motor_asyncio import AsyncIOMotorClient
from config import settings

client = AsyncIOMotorClient(settings.MONGODB_URI)
db = client.torder
store_collection = db.store_info

async def get_database():
    return db

async def get_store_collection():
    return store_collection