"""
Imported the libaries
Extracted data from the DB
Transformed the Data (consolidated JOINS to create an OBT)
Loaded the OBT
from the OBT we created multiple data marts
"""

import pandas as pd
from sqlalchemy import create_engine, text
from credentials import PGDATABASE, PGHOST, PGPASSWORD, PGUSER, PORT


def engine():
    DB_URI = f"postgresql+psycopg2://{PGUSER}:{PGPASSWORD}@{PGHOST}:{PORT}/{PGDATABASE}"
    engine = create_engine(DB_URI)
    return engine

def extract(conn, schema, tables=[]):
    dataframes = {}

    for table in tables:
        query = text(f'SELECT * FROM {schema}.{table};')
        df = pd.read_sql(query, conn)
        print(f'------> Reading {table}')
        dataframes[table] = df

    return dataframes

def transform(dfs: dict, conn):
    customers = dfs['customers']
    orders = dfs['orders']
    order_items =dfs['order_items']
    products = dfs['products']

    print('---> Proceding with Transformation, Starting JOINS ')

    orders_customers = pd.merge(orders, customers, on='customer_id', how='left')
    items_products = pd.merge(order_items, products, on='product_id', how='left')
    full_data = pd.merge(orders_customers, items_products, on='order_id', how='inner')

    print('---> JOIN Completed, OBT Ready')

    print('---> Starting Enrichment to OBT')

    full_data['order_date'] = pd.to_datetime(full_data['order_date'])
    full_data['sales_amount'] = full_data['quantity'] * full_data['unit_price']
    full_data['report_month'] = full_data['order_date'].dt.to_period('M').astype(str)

    print('---> Enrichment Compeleted, Final OBT is ready. Loading to DB')

    full_data.to_sql(name='tinubu_obt', con=conn, schema='prod', if_exists='replace')
    print('---> Succeesfully loaded OBT to DB')

    return full_data

def top_customer_dmart(full_data, conn):
    customer_mart = obt.groupby(['customer_id', 'first_name', 'email', 'country']).agg(
        lifetime_value=('sales_amount', 'sum'),
        total_orders=('order_id', 'nunique'),   
        avg_order_value=('sales_amount', 'mean'), 
        last_seen=('order_date', 'max')    
    ).reset_index()

    print('---> Creating dm_customer_ranking_report')
    top_customers = customer_mart.sort_values('lifetime_value', ascending=False)

    top_customers.to_sql(name='dm_customer_ranking_report', con=conn, schema='prod', if_exists='replace', index=False)

    print('---> Successfully loaded dm_customer_ranking_report to DB')



if __name__ == '__main__':
    connection = engine()
    ingestion = extract(connection, 'raw', tables = ['customers', 'orders', 'order_items', 'products'])
    obt = transform(ingestion, connection)
    top_customer_dmart(obt, connection )
