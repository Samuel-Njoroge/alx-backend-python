import mysql.connector

def paginate_users(page_size, offset):
    """Fetch a single page of users starting from the given offset."""
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='mypassword',
        database='ALX_prodev'
    )
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM user_data LIMIT %s OFFSET %s"
    cursor.execute(query, (page_size, offset))
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    return results

def lazy_paginate(page_size):
    """Generator that lazily paginates user_data using the given page_size."""
    offset = 0
    while True:
        page = paginate_users(page_size, offset)
        if not page:
            break
        yield page
        offset += page_size
