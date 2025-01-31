import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Load environment variables from .env file
load_dotenv()

# Fetch database connection parameters from environment variables
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

def create_table_if_not_exists(connection):
    """
    Creates the detect_data table if it does not exist.
    
    :param connection: Connection object for PostgreSQL.
    """
    create_table_query = """
    CREATE TABLE IF NOT EXISTS detect_data (
        xmin_val FLOAT,
        ymin FLOAT,
        xmax_val FLOAT,
        ymax FLOAT,
        confidence FLOAT,
        class INT,
        name VARCHAR(255),
        image_name VARCHAR(255)
    );
    """
    with connection.cursor() as cursor:
        cursor.execute(create_table_query)
        connection.commit()
    print("Table 'detect_data' is ready.")

def export_data_to_postgres(df, table_name, batch_size= 500):
    """
    Exports a DataFrame to the PostgreSQL database.
    
    :param df: DataFrame to export.
    :param table_name: Name of the table where data will be inserted.
    """
    try:
        # Create a SQLAlchemy engine for PostgreSQL
        engine = create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
        
        # Export the DataFrame to the database (append mode)
        df.to_sql(table_name, engine, if_exists='append', index=False, chunksize=batch_size)
        
        print(f"Data successfully exported to {table_name} table in the database.")
        
    except Exception as e:
        print(f"An error occurred during export: {e}")

def process_and_store_data(file_path, table_name):
    """
    Processes the data and stores it in PostgreSQL.
    
    :param file_path: Path to the CSV file containing data.
    :param table_name: Name of the PostgreSQL table where data will be stored.
    """
    # Step 1: Read the CSV file
    df = pd.read_csv(file_path)

    # Step 2: Ensure the data contains the expected columns
    expected_columns = ["xmin_val", "ymin", "xmax_val", "ymax", "confidence", "class", "name", "image_name"]
    if not all(col in df.columns for col in expected_columns):
        print(f"Error: CSV file does not contain all expected columns: {expected_columns}")
        return
    
    # Step 3: Establish a connection to the database
    connection = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

    # Step 4: Create the table if it doesn't exist
    create_table_if_not_exists(connection)

    # Step 5: Store cleaned data in PostgreSQL
    export_data_to_postgres(df, table_name)

    # Close the database connection
    connection.close()

# Usage
if __name__ == "__main__":
    # Example CSV file path
    file_path = "C:/Users/NurselamHussen-ZOAEt/Downloads/New folder/10 Academy-project/Week-7/all_detections_new.csv"
    
    # Define the PostgreSQL table name where data will be stored
    table_name = "detect_data"
    
    # Process and store the data in the PostgreSQL table
    process_and_store_data(file_path, table_name)













