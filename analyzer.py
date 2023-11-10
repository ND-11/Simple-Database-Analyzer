import sqlalchemy
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
import time
import random
import pandas as pd
import os

# Define the database URL as a constant

EXPORT_FOLDER = 'static/exported_data'


def get_random_table_name(engine):
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    return random.choice(table_names)


def measure_query_execution_time(engine, sql_query):
    try:
        with engine.connect() as connection:
            start_time = time.time()
            result = connection.execute(sql_query)
            end_time = time.time()
            return end_time - start_time
    except Exception as e:
        return f"Error: {e}"


def check_missing_cells(table, session):
    missing_cells_count = 0

    for column in table.c:
        count_null_expression = func.count().filter(column == None)
        null_count = session.query(
            count_null_expression).select_from(table).scalar()
        missing_cells_count += null_count

    return missing_cells_count


def find_duplicate_records(table, session):
    duplicate_records = []

    # Get a list of column names in the table.
    column_names = [column.name for column in table.c]

    # Construct a subquery to find duplicate records.
    subquery = (
        session.query(*table.c)
        .group_by(*table.c)
        .having(func.count() > 1)
        .subquery()
    )

    # Iterate over the results of the subquery and append duplicate records to the list.
    for result in session.query(subquery).all():
        duplicate_records.append(dict(zip(column_names, result)))

    return duplicate_records


def export_table_data(engine, table_name, export_format='csv'):
    try:
        with engine.connect() as connection:
            # Construct a SELECT query to fetch all data from the specified table
            sql_query = f"SELECT * FROM {table_name}"

            # Define the export filename based on the table name and format
            export_filename = os.path.join(
                EXPORT_FOLDER, f"{table_name}.{export_format}")

            # Check if the file already exists, and remove it if it does
            if os.path.exists(export_filename):
                os.remove(export_filename)

            # Execute the query and fetch the data into a Pandas DataFrame
            df = pd.read_sql(sql_query, connection)

            # Create the export folder if it doesn't exist
            if not os.path.exists(EXPORT_FOLDER):
                os.makedirs(EXPORT_FOLDER)

            # Export the DataFrame to the specified format (CSV by default)
            if export_format == 'csv':
                df.to_csv(export_filename, index=False)
            elif export_format == 'excel':
                df.to_excel(export_filename, index=False)

            print(
                f"Data from table '{table_name}' exported to '{export_filename}'")

    except Exception as e:
        print(f"Error: {e}")


def main(DB_URL):

    for filename in os.listdir(EXPORT_FOLDER):
        file_path = os.path.join(EXPORT_FOLDER, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error: {e}")

    results_dict = {}

    try:
        engine = create_engine(DB_URL)
        Session = sessionmaker(bind=engine)
        with Session() as session:
            inspector = inspect(engine)
            table_names = inspector.get_table_names()

            if not table_names:
                print("Database is empty. No tables to analyze.")
                results_dict = {
                    "tables_with_missing_cells": None,
                    "tables_with_duplicate_records": None,
                    "execution_time": None
                }
                return results_dict

            missing_cells_info = {}
            duplicate_records_info = {}

            for table_name in table_names:
                table = sqlalchemy.Table(
                    table_name, sqlalchemy.MetaData(), autoload=True, autoload_with=engine)

                missing_cells_count = check_missing_cells(table, session)
                duplicate_records = find_duplicate_records(table, session)

                if missing_cells_count > 0:
                    missing_cells_info[table_name] = missing_cells_count

                if duplicate_records:
                    duplicate_records_info[table_name] = duplicate_records

            # Store the results in variables
            tables_with_missing_cells = missing_cells_info
            tables_with_duplicate_records = duplicate_records_info

            # You can now use these variables as needed.
            print("Tables with missing cells:")
            for table_name, missing_cells_count in tables_with_missing_cells.items():
                print(
                    f"Table '{table_name}' has {missing_cells_count} missing cells.")

            print("\nTables with duplicate records:")
            for table_name, duplicate_records in tables_with_duplicate_records.items():
                print(
                    f"Table '{table_name}' has the following duplicate records:")
                for record in duplicate_records:
                    print(record)

        # Measure the execution time for a random query
        random_table_name = get_random_table_name(engine)
        sql_query = f"SELECT * FROM {random_table_name}"
        print(f"Random query: {sql_query}")
        execution_time = measure_query_execution_time(engine, sql_query)
        if isinstance(execution_time, float):
            print(
                f"Execution time for random query: {execution_time:.5f} seconds")
        else:
            print(execution_time)

        results_dict = {
            "tables_with_missing_cells": missing_cells_info,
            "tables_with_duplicate_records": duplicate_records_info,
            "execution_time": execution_time
        }

    except Exception as e:
        print(f"Error: {e}")

    # Export data from each table in the database to CSV format
    try:
        engine = create_engine(DB_URL)
        Session = sessionmaker(bind=engine)
        with Session() as session:
            inspector = inspect(engine)
            table_names = inspector.get_table_names()

            for table_name in table_names:
                # Export data from each table in the database to CSV format
                export_table_data(engine, table_name)

    except Exception as e:
        print(f"Error: {e}")

    return results_dict
