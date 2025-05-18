import mysql.connector

def stream_users_in_batches(batch_size):
    """Yields batches of users from the user_data table."""
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='mypassword',
        database='ALX_prodev'
    )
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_data")

    batch = []
    for row in cursor:
        batch.append(row)
        if len(batch) == batch_size:
            yield batch
            batch = []

    if batch:
        yield batch

    cursor.close()
    connection.close()

def batch_processing(batch_size):
    """Yields filtered users over age 25 from each batch."""
    for batch in stream_users_in_batches(batch_size):
        yield [user for user in batch if float(user['age']) > 25]

if __name__ == "__main__":
    for users in batch_processing(5):
        for user in users:
            print(user)
