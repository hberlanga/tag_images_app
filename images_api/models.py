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
    query = ("SELECT p.id, p.size, p.date,GROUP_CONCAT(t.tag ORDER BY t.tag, t.confidence SEPARATOR ',') as g_tags,"+
    "GROUP_CONCAT(t.confidence ORDER BY t.tag, t.confidence SEPARATOR ',') as g_confidences FROM pictures p JOIN tags t ON p.id = t.picture_id")
    if min_date or max_date:
        query = f'{query} WHERE'
        if min_date and max_date:
            query = f'{query} p.date >= "{min_date}" AND p.date <= "{max_date}"'
        elif min_date and not max_date:
            query = f'{query} p.date >= "{min_date}"'
        elif not min_date and max_date:
            query = f'{query} p.date <= "{max_date}"'
    if tags:
         concat_tags = ",".join([f'"{x}"' for x in tags])
         query = f'{query} {"AND" if (min_date or max_date) else "WHERE"} t.picture_id IN (SELECT t2.picture_id FROM tags t2 WHERE t2.tag IN ({concat_tags}))'    
    query = f'{query} GROUP BY t.picture_id'
    with engine.connect() as conn:
        result = conn.execute(text(query))
        columns = result.keys()
        return [
            dict(zip(columns, row))
            for row in result
        ]

def get_picture(id):
    query = ("SELECT p.id, p.path,p.size,p.date,GROUP_CONCAT(t.tag ORDER BY t.tag, t.confidence SEPARATOR ',') as g_tags,"+
    "GROUP_CONCAT(t.confidence ORDER BY t.tag, t.confidence SEPARATOR ',') as g_confidences FROM pictures p JOIN tags t ON p.id = t.picture_id")
    query = f"{query} WHERE p.id = '{id}'"
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
