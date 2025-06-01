import asyncio
import aiosqlite

async def async_fetch_users():
    async with aiosqlite.connect('users.db') as db:
        cursor = await db.execute("SELECT * FROM users")
        results = await cursor.fetchall()
        await cursor.close()
        return results

async def async_fetch_older_users():
    async with aiosqlite.connect('users.db') as db:
        cursor = await db.execute("SELECT * FROM users WHERE age > 40")
        results = await cursor.fetchall()
        await cursor.close()
        return results

async def fetch_concurrently():
    # Must have `await asyncio.gather(...)`
    results = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )
    print(results)

# Call `asyncio.run(fetch_concurrently())`
asyncio.run(fetch_concurrently())
