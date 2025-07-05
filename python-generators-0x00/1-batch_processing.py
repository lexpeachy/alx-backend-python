import mysql.connector
from typing import Dict, Generator, List

def stream_users_in_batches(batch_size: int) -> Generator[List[Dict[str, str | int]], None, None]:
    """
    Generator function that streams rows from user_data table in batches.
    
    Args:
        batch_size: Number of rows to fetch at a time
        
    Yields:
        List[Dict]: A batch of rows from user_data table, each row as a dictionary
    """
    connection = None
    cursor = None
    
    try:
        # Connect to the database
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='ALX_prodev'
        )
        
        # Create a server-side cursor (more memory efficient)
        cursor = connection.cursor(dictionary=True)
        
        # Execute the query
        cursor.execute("SELECT * FROM user_data")
        
        # Stream rows in batches
        while True:
            batch = cursor.fetchmany(batch_size)
            if not batch:
                break
            yield batch
            
    except mysql.connector.Error as e:
        print(f"Database error: {e}", file=sys.stderr)
    finally:
        # Clean up resources
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def batch_processing(batch_size: int = 50) -> None:
    """
    Processes user data in batches, filtering for users over 25 years old.
    
    Args:
        batch_size: Number of users to process at a time (default: 50)
    """
    # Loop 1: Iterate through batches
    for batch in stream_users_in_batches(batch_size):
        # Loop 2: Process each user in the batch
        for user in batch:
            # Loop 3: Filter users over 25
            if user['age'] > 25:
                print(user)
