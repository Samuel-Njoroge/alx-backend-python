import time
import sqlite3 
import functools

query_cache = {}

# Decorator to manage DB connection
def with_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            return func(conn, *args, **kwargs)
        finally:
            conn.close()
    return wrapper

# Decorator to cache query results
def cache_query(func):
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        # Extract the SQL query from args or kwargs
        query = kwargs.get('query')
        if query is None and len(args) > 0:
            query = args[0]  # first non-conn positional argument
        if query in query_cache:
            print("[Cache] Returning cached result.")
            return query_cache[query]
        result = func(conn, *args, **kwargs)
        query_cache[query] = result
        return result
    return wrapper

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

# Cache the result
users = fetch_users_with_cache(query="SELECT * FROM users")
print(users)

# Use the cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users")
print(users_again)
