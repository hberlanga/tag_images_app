import base64
import datetime
from collections import defaultdict 
from flask import Blueprint, request, make_response
from . import controller

bp = Blueprint('images', __name__, url_prefix='/api')

def validate_post_image_request(request):
    if not request.is_json:
        raise TypeError("Request body should be JSON")
    data = str(request.json["data"])
    if not data or data == '':
        raise ValueError("Empty 'data' value. Should be a base64 encoded image")
    data_bytes = bytes(data, 'ascii')
    if base64.b64encode(base64.b64decode(data_bytes)) != data_bytes:
        raise ValueError("'data' value shoul be a valid base64 string")
    
def validate_get_images_params(min_date, max_date):
    if min_date is not None:
        validate_date_param(min_date)
    if max_date is not None:
        validate_date_param(max_date)
    
def validate_date_param(str_date):
    try:
        datetime.datetime.fromisoformat(str_date)
    except Exception as e:
        print(e)
        raise ValueError("Invalid date format")
    
def validate_get_tags_params(min_date, max_date):
    if min_date is not None:
        validate_date_param(min_date)
    if max_date is not None:
        validate_date_param(max_date)
    
def zip_tags(results, filter_tags):
    final_result = []
    for row in results:
        tags = []
        if row["g_tags"] is not None:
            if filter_tags is not None and not set(filter_tags).issubset(row["g_tags"].split(",")):
                continue
            tags_confidences = zip(row["g_tags"].split(","),row["g_confidences"].split(","))
            for tag,confidence in tags_confidences:
                tags.append({
                    "tag" : tag,
                    "confidence" : confidence
                })
        final_result.append({
            "id" : row["id"],
            "size" : row["size"],
            "date" : row["date"],
            "tags" :  tags
        })
    return final_result 

@bp.post("/images")
def post_image():
    try:
        validate_post_image_request(request)
    except Exception as e:
        return make_response({
            "message" : str(e)
        },400)
    min_confidence = int(request.args.get("min_confidence", "80"))
    base64_str = str(request.json["data"])
    result = controller.process_post_image(base64_str, min_confidence)
    (id, size, date, tags, data) = result
    response = {
        "id" : id,
        "size" : size,
        "date" : date,
        "tags" : tags,
        "data" : data
    }
    return make_response(response, 201)

  
@bp.get("/images")
def get_images():
    min_date = request.args.get("min_date")
    max_date = request.args.get("max_date")
    tags = request.args.get("tags","")
    try:
        validate_get_images_params(min_date, max_date)
    except Exception as e:
        return make_response({
            "message" : str(e)
        },400)
    tags = tags.split(",") if len(tags) > 0 else None
    results = controller.process_get_images(min_date, max_date, tags)
    return zip_tags(results, tags)

@bp.get("/images/<id>")
def get_image(id):
    image = controller.process_get_image(id)
    if image is not None:
        (result, b64_img) = image
        response = zip_tags(result, None)[0]
        response["data"] = b64_img
        return response
    else:
        return make_response({
            "message" : f"Image with ID '{id}' not found"
        },404)


@bp.get("/tags")
def get_tags():
    min_date = request.args.get("min_date")
    max_date = request.args.get("max_date")
    try:
        validate_get_tags_params(min_date, max_date)
    except Exception as e:
        return make_response({
            "message" : str(e)
        },400)
    return controller.process_get_tags(min_date, max_date)
