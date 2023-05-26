# Práctica 2. Diseño y despliegue de la interfaz de notificaciones

## Consideraciones de diseño

La interfaz de notificaciones se ha implementado en Python 3.10 usando FastAPI, la libreria SQLAlchemy ORM (Object-Relational Mapper) y SQLite (se ha seguido el tutorial [SQL (Relational) Databases](https://fastapi.tiangolo.com/es/tutorial/sql-databases). En concreto:

- FastAPI es un marco para Python que permite la construcción rápida de APIs usando anotaciones de tipos estándar de Python. Es compatible con estándares como OpenAPI y JSON Schema.
- SQLAlquemy ORM es una librería que implementa el patrón ORM (Object-Relational Mapper) con el que se consigue convertir (o mapear) automáticamente los objetos Python de la aplicación en estructuras de una base de datos relacional (SQL).
- SQLite es una base de datos relacional sencilla que usa un único fichero para el almacenamiento persistente de los datos.

El esquema de la base de datos es muy sencillo pues consta de dos tablas: **Notificaciones** para guardar la información sobre notificaciones y **Usuarios** para la generación de tokens JWT. Se incluye también una secuencia para la generación automática de identificadores para las nuevas notificaciones.

Las peticiones HTTP pueden incluir un token JWT en cuyo caso se autorizan si el usuario aparece en la base de datos, rechazándolas en caso contrario. El token JWT debe aparecer en la cabecera **authorization** de la petición HTTP como sigue:

```sh
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJBT1MgMjAyMyAtIEFQSSBOb3RpZm...
```
Para facilitar la integración con los otros equipos las peticiones HTTP que incluyen tokens JWT son autorizadas siempre aunque en un entorno de producción se deberían de rechazar.

Los tokens JWT pueden generase con el comando:
```sh
curl -X POST http://<servidor>:<puerto>/login ....
```
Este comando envia una petición HTTP de tipo POST al servidor incluyendo en el cuerpo un documento JSON con el nombre del usuario y su contraseña, y el servidor devuelve en la respuesta:
- Un token JWT de acceso con una caducidad de 7 minutos
- Un token JWT de refresco con una caducidad de 7 días

El usuario que aparece en el ejemplo ha sido preregistrado en la aplicación y puede ser usado para generar nuevos tokens JWT.

Las respuestas HTTP del servidor incluyen cabeceras **etag** que pueden ser usadas por los clientes en las peticiones HTTP subsiguientes. La etiqueta **etag** generado es la firma MD5 del documento JSON devuelto en la respuesta.

Finalmente, el servidor soporta CORS (Cross-Origin Resource Sharing), una recomendación del consorcio W3C que define un mecanismo de seguridad que pueden aplicar los clientes de una interfaz Web (típicamente navegadores) para bloquear el acceso a recursos incluidos en las respuestas que no han sido autorizados por el servidor. Esta política no aplica si el recurso está alojado en un origen distinto al de la petición, es decir, distinto protocolo, dominio o puerto.

## Imagen

La imagen de la aplicación se encuentra disponible en el siguiente [enlace a DockerHub](https://hub.docker.com/r/acarrasco2000/aos2023_notificaciones). La imagen incluye el código del servidor (directorio /app/server) y el fichero SQLite con la base de datos (fichero /app/server/sql_app.db) con los siguientes datos iniciales:
- Notificaciones con identificadores "1234-1234-12" y "1234-1234-13"
- Usuario con nombre "alejandro.carrasco.aragon@alumnos.upm.es" y hash de contraseña "secret"

Para arrancar la aplicación podemos usar el comando:
```sh
docker run --name <nombre> acarrasco2000/aos2023_notificaciones:v1
```
El servidor escucha en el host "0.0.0.0" y puerto 80 del contenedor Docker. Usar la opción "-p" del comando anterior para seleccionar host o puerto distintos en la máquina local.

## Despliegue de servicios mediante Docker Compose

[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)

   [dill]: <https://github.com/joemccann/dillinger>
