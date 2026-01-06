#!/usr/bin/env python3
"""Test if we can search the local Qdrant database."""
import asyncio
from core.retriever import search, get_sites

async def main():
    print("Testing Qdrant local database search...\n")
    
    # Test 1: Get all sites
    print("1. Getting all sites...")
    try:
        sites = await get_sites(endpoint_name="qdrant_local")
        print(f"   ✅ Found {len(sites)} sites: {sites}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test 2: Search for podcasts
    print("\n2. Searching for 'podcast episodes'...")
    try:
        results = await search("podcast episodes", site="all", endpoint_name="qdrant_local", num_results=5)
        print(f"   ✅ Found {len(results)} results:")
        for i, result in enumerate(results[:3], 1):
            url, json_str, name, site = result
            print(f"      {i}. {name} (site: {site})")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
