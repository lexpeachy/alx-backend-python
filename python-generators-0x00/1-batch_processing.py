import mysql.connector
from typing import Generator, Dict, List

def stream_users_in_batches(batch_size: int) -> Generator[List[Dict[str, str | int]], None, None]:
    """Stream users from database in batches using yield"""
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='ALX_prodev'
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_data")
    
    while True:
        batch = cursor.fetchmany(batch_size)
        if not batch:
            cursor.close()
            conn.close()
            break
        yield batch  # Using yield to make this a generator

def batch_processing(batch_size: int = 50) -> None:
    """Process batches of users and filter those over 25"""
    for batch in stream_users_in_batches(batch_size):  # First loop
        for user in batch:  # Second loop
            if user['age'] > 25:  # Filter condition (not counted as a full loop)
                print(user)
