import asyncpg
from config import DB_NAME, DB_USER, DB_PASSW, DB_HOST, DB_PORT


async def est_connection():
    return await asyncpg.connect(
                user=DB_USER,
                password=DB_PASSW,
                database=DB_NAME,
                host=DB_HOST,
                port=DB_PORT
            )


async def create_table(connection):
    await connection.execute('''
        CREATE TABLE IF NOT EXISTS vip_users (
        id serial PRIMARY KEY,
        tg_id bigint UNIQUE,
        viz_account name,
        regular_key text,
        reward_size numeric
        )
    ''')
