async def create_table(connection):
    await connection.execute('''
        CREATE TABLE IF NOT EXISTS vip_users (
        id serial PRIMARY KEY,
        tg_id integer,
        viz_account name,
        regular_key text,
        reward_size numeric
        )
    ''')
