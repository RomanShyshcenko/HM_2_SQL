import uuid
import random
from datetime import datetime, timedelta

import psycopg2
from psycopg2.extras import execute_values
from faker import Faker


# Connection settings
HOST = 'localhost' # put your credentials here
USER = 'postgres' # put your credentials here
PASSWORD = '1' # put your credentials here
DATABASE = 'bank' # put your credentials here
PORT = '5432' # put your credentials here

# Data volume settings
CLIENTS_COUNT = 10_000
ACCOUNTS_COUNT = 10_000
TRANSACTIONS_COUNT = 15_000
CHUNK_SIZE = 10_000

fake = Faker()


def insert_clients(cursor):
    print("Inserting into clients...")

    client_insert_query = """
        INSERT INTO clients
            (ClientName, BCAName)
        VALUES %s
        RETURNING ClientID
    """

    client_ids = []

    for start in range(0, CLIENTS_COUNT, CHUNK_SIZE):
        current_chunk_size = min(CHUNK_SIZE, CLIENTS_COUNT - start)

        clients_data = []
        for _ in range(current_chunk_size):

            clients_data.append(
                (
                    
                    fake.name(),
                    fake.name(),
                )
            )

        execute_values(cursor, client_insert_query, clients_data)

        chunk_ids = [row[0] for row in cursor.fetchall()]
        client_ids.extend(chunk_ids)

        print(f"Inserted {start + current_chunk_size} rows into clients...")

    print("Inserted into clients.")
    return client_ids


def insert_accounts(cursor,client_ids):
    print("Inserting into accounts...")

    account_insert_query = """
        INSERT INTO accounts
            (ClientID, balance, currency)
        VALUES %s
        RETURNING AccountID
    """

    account_ids=[]

    for start in range(0, ACCOUNTS_COUNT, CHUNK_SIZE):
        current_chunk_size = min(CHUNK_SIZE, ACCOUNTS_COUNT - start)

        accounts_data = [
        (
            random.choice(client_ids),
            round(random.uniform (50, 100000000),2),
            random.choice(['UAH', 'EUR','USD']),
        )
        for _ in range(current_chunk_size)
    ]

        execute_values(cursor, account_insert_query, accounts_data)

        chunk_ids = [row[0] for row in cursor.fetchall()]
        account_ids.extend(chunk_ids)

    print(f"Inserted {start + current_chunk_size} rows into accounts...")

    print("Inserted into accounts.")
    return account_ids

def insert_transactions(cursor, account_ids):
    print("Inserting into transactions...")

    transaction_insert_query = """
        INSERT INTO transactions
            (SenderID, ReceiverID, money_amount, TransactionDate)
        VALUES %s
    """

    transaction_date_start = datetime.now() - timedelta(days=365 * 5)

    for start in range(0, TRANSACTIONS_COUNT, CHUNK_SIZE):
        current_chunk_size = min(CHUNK_SIZE, TRANSACTIONS_COUNT - start)

        transactions_data = []

        for _ in range(current_chunk_size):
            sender = random.choice(account_ids)
            receiver = random.choice(account_ids)
            
            while sender==receiver:
                receiver=random.choice(account_ids)

            transactions_data.append(
            (
                sender,
                receiver,
                round(random.uniform (50, 100000000),2),
                transaction_date_start + timedelta(days=random.randint(0, 365 * 5)),
                
            )
            
            )

        execute_values(cursor, transaction_insert_query, transactions_data)
        print(f"Inserted {start + current_chunk_size} rows into transactions...")

    print("Inserted into transactions.")


def main():
    connection = psycopg2.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        dbname=DATABASE,
        port=PORT,
    )

    try:
        with connection:
            with connection.cursor() as cursor:
                client_ids = insert_clients(cursor)
                account_ids = insert_accounts(cursor,client_ids)
                insert_transactions(cursor, account_ids)

    finally:
        connection.close()


if __name__ == "__main__":
    main()
