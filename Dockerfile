FROM python:3.11

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./images_api ./images_api

EXPOSE 80

CMD ["waitress-serve", "--host=0.0.0.0", "--port=80", "--call", "images_api:create_app"]