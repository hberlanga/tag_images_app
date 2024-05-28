from sqlalchemy import create_engine, text

engine = create_engine("mysql+pymysql://mbit:mbit@db/Pictures")

PICTURES_COLUMNS = ('id', 'path', 'date', 'size')
TAGS_COLUMNS = ('tag', 'picture_id', 'confidence', 'date')

def start_transaction():
    return engine.connect()

def end_transaction(conn):
    conn.commit()
    conn.close()

def rollback_transaction(conn):
    conn.rollback()
    conn.close()

"""
Inserta un nuevo registro en la tabla pictures
"""
def insert_pictures(conn, values):
    (id, path, date, size) = values
    conn.execute(text(f"INSERT INTO pictures VALUES ('{id}', '{path}',{size}, '{date}')"))
    return dict(zip(PICTURES_COLUMNS, values))
"""
Consulta sobre la tabla pictures
"""
def query_pictures(min_date, max_date, tags):
    if tags:
        query = "SELECT * FROM pictures p JOIN tags t ON p.id = t.picture_id"
    else:
        query = "SELECT * FROM pictures p"
    if min_date or max_date:
        query = f'{query} WHERE'
        if min_date and max_date:
            query = f'{query} "{min_date}" <= p.date >= "{max_date}"'
        elif min_date and not max_date:
            query = f'{query} " p.date >= "{min_date}"'
        elif not min_date and max_date:
            query = f'{query} " p.date <= "{max_date}"'
    #if (min_date or max_date) and tags:
    #     query = f'{query} AND t.tag IN ({",".join([f'"{x}"' for x in tags])})'    
    print(f'Query => {query}')
    with engine.connect() as conn:
        result = conn.execute(text(query))
        columns = result.keys()
        return [
            dict(zip(columns, row))
            for row in result
        ]

def get_picture(id):
    query = f"SELECT * FROM pictures p JOIN tags t ON p.id = t.picture_id where p.id = '{id}'"
    with engine.connect() as conn:
        result = conn.execute(text(query))
        columns = result.keys()
        return [
            dict(zip(columns, row))
            for row in result
        ]

def insert_tags(conn, values):
    (tag, picture_id, confidence, date) = values
    conn.execute(text(f"INSERT INTO tags VALUES ('{tag}','{picture_id}', {confidence}, '{date}')"))
    return dict(zip(TAGS_COLUMNS, values))

def get_tags(min_date, max_date):
    query = "SELECT tag, max(confidence) as max_confidence, min(confidence) as min_confidence, avg(confidence) as mean_confidence, count(1) as n_images FROM tags"
    if min_date or max_date:
        query = f'{query} WHERE'
        if min_date and max_date:
            query = f'{query} "{min_date}" <= p.date >= "{max_date}"'
        elif min_date and not max_date:
            query = f'{query} " p.date >= "{min_date}"'
        elif not min_date and max_date:
            query = f'{query} " p.date <= "{max_date}"'
    query = f'{query} GROUP BY tag'
    with engine.connect() as conn:
        result = conn.execute(text(query))
        columns = result.keys()
        return [
            dict(zip(columns, row))
            for row in result
        ]
