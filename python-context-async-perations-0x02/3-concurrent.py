import asyncio
import aiosqlite

# Fetch all users
async def async_fetch_users():
    async with aiosqlite.connect('users.db') as db:
        cursor = await db.execute("SELECT * FROM users")
        results = await cursor.fetchall()
        await cursor.close()
        print("All users:", results)
        return results

# Fetch users older than 40
async def async_fetch_older_users():
    async with aiosqlite.connect('users.db') as db:
        cursor = await db.execute("SELECT * FROM users WHERE age > 40")
        results = await cursor.fetchall()
        await cursor.close()
        print("Users older than 40:", results)
