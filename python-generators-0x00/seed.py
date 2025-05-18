import mysql.connector
import csv
import uuid

def connect_db():
    """Connect to MySQL server (without specifying a DB)."""
    return mysql.connector.connect(
        host='localhost',
        user='root',       
        password='mypassword',       
        autocommit=True
    )

def create_database(connection):
    """Create the ALX_prodev database if it doesn't exist."""
    cursor = connection.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
    cursor.close()

def connect_to_prodev():
    """Connect to the ALX_prodev database."""
    return mysql.connector.connect(
        host='localhost',
        user='root',       
        password='mypassword',  
        database='ALX_prodev',
        autocommit=True
    )

def create_table(connection):
    """Create the user_data table if it doesn't exist."""
    cursor = connection.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_data (
        user_id CHAR(36) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        age DECIMAL NOT NULL,
        INDEX idx_user_id (user_id)
    )
    """)
    cursor.close()

def insert_data(connection, data):
    """Insert data into user_data if the user_id does not already exist."""
    cursor = connection.cursor()

    for row in data:
        user_id = row.get('user_id')
        # If no user_id given, generate a new UUID
        if not user_id:
            user_id = str(uuid.uuid4())

        name = row['name']
        email = row['email']
        age = row['age']

        # Check if user_id already exists
        cursor.execute("SELECT COUNT(*) FROM user_data WHERE user_id = %s", (user_id,))
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO user_data (user_id, name, email, age)
                VALUES (%s, %s, %s, %s)
            """, (user_id, name, email, age))

    connection.commit()
    cursor.close()

def read_csv(file_path):
    """Read CSV file and return list of dictionaries."""
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        return list(reader)

def main():
    # Connect to MySQL server and create database
    connection = connect_db()
    create_database(connection)
    connection.close()

    # Connect to ALX_prodev database
    prodev_conn = connect_to_prodev()

    # Create table if not exists
    create_table(prodev_conn)

    # Read data from CSV
    data = read_csv('user_data.csv')

    # Insert data
    insert_data(prodev_conn, data)

    prodev_conn.close()
    print("Database seeded successfully.")

if __name__ == '__main__':
    main()
