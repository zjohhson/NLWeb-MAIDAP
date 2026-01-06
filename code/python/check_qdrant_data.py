#!/usr/bin/env python3
"""Quick script to check what data is in local Qdrant database."""
import asyncio
from retrieval_providers.qdrant import QdrantVectorClient

async def main():
    print("Checking local Qdrant database...")
    client = QdrantVectorClient('qdrant_local')
    qc = await client._get_qdrant_client()
    
    collection_name = client.default_collection_name
    print(f"\nCollection: {collection_name}")
    
    # Check if collection exists
    exists = await client.collection_exists(collection_name)
    if not exists:
        print("❌ Collection does not exist!")
        return
    
    # Get collection info
    info = await qc.get_collection(collection_name)
    print(f"✅ Points in database: {info.points_count}")
    
    if info.points_count > 0:
        # Get a few sample points
        result = await qc.scroll(
            collection_name=collection_name,
            limit=10,
            with_payload=True,
            with_vectors=False
        )
        
        points = result[0]
        print(f"\nSample documents:")
        for i, point in enumerate(points[:5], 1):
            payload = point.payload
            print(f"\n{i}. Site: {payload.get('site', 'unknown')}")
            print(f"   Name: {payload.get('name', 'No name')}")
            print(f"   URL: {payload.get('url', 'No URL')}")

if __name__ == "__main__":
    asyncio.run(main())
