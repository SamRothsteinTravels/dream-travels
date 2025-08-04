#!/usr/bin/env python3
"""
Test MongoDB Connection for Dream Travels
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def test_mongodb_connection():
    """Test the MongoDB Atlas connection"""
    
    # Your MongoDB connection string
    MONGO_URL = "mongodb+srv://65willswat:rodxa4-hebdoc-qiwFyz@cluster0.yin7cfx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    DB_NAME = "dream_travels_db"
    
    try:
        print("🔍 Testing MongoDB Atlas connection...")
        
        # Create client
        client = AsyncIOMotorClient(MONGO_URL)
        
        # Test connection
        await client.admin.command('ping')
        print("✅ Successfully connected to MongoDB Atlas!")
        
        # Test database access
        db = client[DB_NAME]
        collections = await db.list_collection_names()
        print(f"✅ Database '{DB_NAME}' accessible")
        print(f"📊 Collections found: {collections if collections else 'None (new database)'}")
        
        # Insert a test document
        test_collection = db.test_connection
        result = await test_collection.insert_one({
            "test": "Dream Travels connection test",
            "timestamp": "2025-01-01T00:00:00Z",
            "status": "success"
        })
        print(f"✅ Test document inserted with ID: {result.inserted_id}")
        
        # Read the test document back
        doc = await test_collection.find_one({"_id": result.inserted_id})
        if doc:
            print("✅ Test document retrieved successfully")
        
        # Clean up test document
        await test_collection.delete_one({"_id": result.inserted_id})
        print("🧹 Test document cleaned up")
        
        print("\n🎉 MongoDB Atlas is ready for Dream Travels deployment!")
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Check your MongoDB Atlas cluster is active")
        print("2. Verify Network Access allows 0.0.0.0/0")
        print("3. Ensure database user has read/write permissions")
        print("4. Double-check your connection string password")
    
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    asyncio.run(test_mongodb_connection())