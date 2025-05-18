import mysql.connector

def stream_users():
    """Generator that yields rows from the user_data table one at a time."""
    connection = mysql.connector.connect(
        host='localhost',
        user='root',      
        password='mypassword',       
        database='ALX_prodev'
    )
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_data")

    for row in cursor:
        yield row

    cursor.close()
    connection.close()
