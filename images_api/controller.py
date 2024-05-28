from . import models
from images_api.utils.transactional import transactional
from imagekitio import ImageKit
import base64
import os
import requests
import json
import uuid
import datetime


def import_credentials():
    if not os.environ['CREDENTIALS_FILEPATH']:
        raise ValueError("Env var 'CREDENTIALS_FILEPATH' not defined")
    with open(os.environ['CREDENTIALS_FILEPATH'], "r") as file:
        return json.load(file)
    
credentials = import_credentials()

def get_imagekit_client():
    return ImageKit(
        public_key=credentials["imagekit"]["publicKey"],
        private_key=credentials["imagekit"]["privateKey"],
        url_endpoint=credentials["imagekit"]["url"]
    )

def get_imagga_credentials():
    return (credentials["imagga"]["apiKey"], credentials["imagga"]["apiSecret"])

def generate_uuid():
    return uuid.uuid4()

@transactional
def process_post_image(base64_str, min_confidence, conn):
    id = str(generate_uuid())
    #Upload file
    uploaded_image = upload_image(base64_str, id)
    #Get tags related with image
    tags = get_tags_image(uploaded_image.url, min_confidence)
    delete_image(uploaded_image.file_id)
    #Save image on disk and DB
    img_bytes = base64.b64decode(base64_str.encode())
    path = save_image_on_disk(img_bytes, id)
    size = os.stat(path).st_size / 1024
    image_row = save_image_db(conn, id, path, size)
    #Save tags on DB
    save_tags_db(conn, image_row, tags)
    return (id, size, image_row["date"], tags, base64_str)

def process_get_images(min_date, max_date, tags):
    return models.query_pictures(min_date, max_date, tags)

def process_get_image(id):
    db_row = models.get_picture(id)
    if db_row:
        b64_image = get_image_from_disk(db_row[0]["path"])
        return (db_row,b64_image)
    else:
        return None
    
def process_get_tags(min_date, max_date):
    return models.get_tags(min_date, max_date)

def get_image_from_disk(path):
    with open(path,"rb") as file:
        return base64.b64encode(file.read()).decode('utf-8')


"""
Recibe la imagen en base64 y la sube a imagekit, devolviendo la URL publica 
"""
def upload_image(b64_image, id):
    imageKit = get_imagekit_client()
    return imageKit.upload(file=b64_image, file_name=id)

"""
Consume una API externa que va a tagear la imagen que le pasemos via URL.
Filtra los tags por el minimo de confianza establecido y devuelve un listado
con los tags
"""
def get_tags_image(url, min_confidence):
    imagga_credentials = get_imagga_credentials()
    res = requests.get(f"https://api.imagga.com/v2/tags?image_url={url}", auth=imagga_credentials)
    return [
        {
            "tag": t["tag"]["en"],
            "confidence": round(float(t["confidence"]), 4)
        }
        for t in res.json()["result"]["tags"]
        if t["confidence"] > min_confidence
    ]

"""
Borra la imagen alojada en imagekit
"""
def delete_image(id):
    imageKit = get_imagekit_client()
    imageKit.delete_file(file_id=id)

"""
Aloja la imagen en disco y devuelve el path
"""
def save_image_on_disk(image, id):
    base_path = os.path.join(os.getcwd(), 'images')
    os.makedirs(base_path, exist_ok=True)
    path = f"{base_path}/{id}"
    with open(path,"wb") as file:
        file.write(image)
    return path

"""
Calcula la fecha de insercion y llama a models para guardar el registro en BD. 
Devuelve la dict con el registro creado
"""
def save_image_db(conn, id, path, size):
    date = datetime.datetime.now().replace(microsecond=0).isoformat()
    #Force to replace '\' (Windows env)
    path = str(path).replace('\\','/')
    values = (id, path, date, size)
    return models.insert_pictures(conn, values)

"""
Recorre la lista de tags y llama a models para guardar el registro en BD. 
Devuelve la dict con el registro creado
"""
def save_tags_db(conn, image_values, tags):
    result = []
    for tag in tags:
        tag_values = (tag["tag"], image_values["id"], tag["confidence"], image_values["date"])
        result.append(models.insert_tags(conn, tag_values))
    return result
