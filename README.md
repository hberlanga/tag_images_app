# Proyecto de consolidación MDE mbit Módulo 2

Para arrancar la aplicación:

Construir la imagen de la base de datos MySQL con el fichero DDL para crear el modelo de tablas. Desde la carpeta "/sql" ejecutar
  ```
  docker build . mysql_pictures:1.0.0
  ``` 
Crear un fichero "credentials.json" en alguna ruta dentro de la carpeta "images_api". El fichero debe tener la siguiente estrcutura
  ```
  {
    "imagekit" : {
        "publicKey" : <<PUBLIC_KEY>>,
        "privateKey" : <<PRIVATE_KEY>>,
        "url" : <<URL>>
    },
    "imagga" : {
        "apiKey" : <<API_KEY>>,
        "apiSecret" : <<API_SECRET>>
    }
}
  ``` 
Construir la imagen del servidor REST. Desde la carpeta raíz del proyecto, ejecutar
  ```
  docker build . server_images:1.0.0
  ``` 
Desde el directorio raíz del proyecto lanzar el comando
  ```
  docker-compose up -d
  ```
La app ya es accesible desde el puerto 80 de nuestra propia máquina.
