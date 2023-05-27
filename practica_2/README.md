# Práctica 2. Diseño y despliegue del servicio de Notificaciones

## Consideraciones de diseño

El servicio de Notificaciones es un servidor HTTP que implementa la interfaz especificada en OpenAPI en la parte 1 de la práctica y que se puede consultar [aquí][ifz]. Se ha implementado en Python 3.10 usando FastAPI, la libreria SQLAlchemy ORM (Object-Relational Mapper) y SQLite (se ha seguido el tutorial [SQL (Relational) Databases][tutorial]. En concreto:

- FastAPI es un marco para Python que permite la construcción rápida de APIs usando anotaciones de tipos estándar de Python. Es compatible con estándares como OpenAPI y JSON Schema.
- SQLAlquemy ORM es una librería que implementa el patrón ORM (Object-Relational Mapper) con el que se consigue convertir (o mapear) automáticamente los objetos Python de la aplicación en estructuras de una base de datos relacional (SQL).
- SQLite es una base de datos relacional sencilla que usa un único fichero para el almacenamiento persistente de los datos.

El esquema de la base de datos es muy sencillo pues consta de dos tablas: **Notificaciones** para guardar la información sobre notificaciones y **Usuarios** para la generación de tokens JWT. Se incluye también una secuencia para la generación automática de identificadores para las nuevas notificaciones.

El servidor HTTP puede recibir peticiones que incluyan tokens JWT. Estas peticiones se autorizan si el token JWT es válido y se ha generado para un usuario registrado en la base de datos, rechazándose en caso contrario. El token JWT debe aparecer en la cabecera **authorization** de la petición HTTP de la siguiente forma:

```sh
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJBT1MgMjAyMyAtIEFQSSBOb3RpZm...
```
Los tokens JWT pueden generase con el comando:
```sh
curl -X "POST" "http://<servidor>:<puerto>/login" -H "accept: */*" -H "Content-Type: application/x-www-form-urlencoded" -d "username=demo&password=secret"
```
donde `http:<servidor>:<puerto>` es la URL base del servidor de Notificaciones (`http://localhost:4013`) en el despliegue local. Este comando envía una petición POST que incluye en el "body" un formulario post de OAuth 2.0 con el usuario y la contraseña del usuario demo, devolviendo en la respuesta:
- Un token JWT de acceso con una caducidad de 7 minutos
- Un token JWT de refresco con una caducidad de 7 días

Este es un ejemplo del documento JSON incluido en la respuesta a esta petición:
```sh
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJBT1MgMjAyMyAtIEFQSSBOb3RpZmljYWNpb25lcyIsImF1ZCI6IkFPUyBVUE0iLCJzdWIiOiJhbGVqYW5kcm8uY2FycmFzY28uYXJhZ29uQGFsdW1ub3MudXBtLmVzIiwiZXhwIjoxNjg1MjA5NDY5LjI4Mzg4NTcsImlhdCI6MTY4NTIwNzY2OS4yODM4ODU3fQ.bGK9RSOCaw76sv6sRYZdznMCBfN7AJdshBmyzJzVoYE",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJBT1MgMjAyMyAtIEFQSSBOb3RpZmljYWNpb25lcyIsImF1ZCI6IkFPUyBVUE0iLCJzdWIiOiJhbGVqYW5kcm8uY2FycmFzY28uYXJhZ29uQGFsdW1ub3MudXBtLmVzIiwiZXhwIjoxNjg1ODEyNDY5LjI4Mzg4NTcsImlhdCI6MTY4NTIwNzY2OS4yODM4ODU3fQ.7m6oUqkbp1Fth3BLwCblikXoj9GF136Ge_VSbXAIA4I",
  "token_type": "bearer"
}
```
Más detalles sobre el marco de autenticación OAuth 2.0 se pueden consultar [aquí][OAuth 2.0].

Para facilitar la integración con los otros equipos la autorización con tokens JWT es opcional, es decir, el servicio no rechaza peticiones que no lo incluyan. En un entorno real se debería requerir siempre esta autorización.

Las respuestas HTTP del servidor incluyen cabeceras `etag` que pueden ser usadas por los clientes en las peticiones HTTP subsiguientes. La etiqueta `etag` generada es la firma MD5 del documento JSON devuelto en la respuesta.

Finalmente, el servidor soporta CORS (Cross-Origin Resource Sharing), una recomendación del consorcio W3C que define un mecanismo de seguridad que pueden aplicar los clientes de una interfaz Web (típicamente navegadores) para bloquear el acceso a recursos incluidos en las respuestas que no han sido autorizados por el servidor. Esta política sólo aplica si el recurso está alojado en un origen distinto al de la petición, es decir, distinto protocolo, dominio o puerto.

## Imagen

La imagen de la aplicación se encuentra disponible en el siguiente [enlace a DockerHub][imagen] y usa la etiqueta `v1`. Si se prefiere se puede descargar con el comando:
```sh
docker pull acarrasco2000/aos2023-notificaciones:v1
```
La imagen se ha generado con el comando:
```sh
docker build -t acarrasco2000/aos2023-notificaciones:v1 -f <Dockerfile>
```
donde <Dockerfile> es el fichero `Dockerfile` del proyecto que se puede consultar [aquí][docker].

La imagen incluye el código del servidor (directorio /app/server) y el fichero SQLite con la base de datos (fichero /app/server/sql_app.db) con los siguientes datos iniciales:
- Notificaciones con identificadores "1234-1234-12" y "1234-1234-13"
- Usuario con nombre "demo" y hash de su contraseña ('secret')

Para arrancar la aplicación podemos usar el comando:
```sh
docker run --name <nombre> -p 80:4010 acarrasco2000/aos2023-notificaciones:v1
```

tras lo cual se puede acceder en la dirección `http://localhost:80` (en la opción -p se puede elegir un puerto en la máquina local distinto a 80). FastAPI genera automáticamente la documentación de la interfaz en OpenAI proporcionando una UI similar a la de Swagger y que puede accederse con la dirección `http://localhost:80/docs`.

**NOTA**: Las direcciones base de los servicios del resto del Taller pueden cambiarse a través de las variables de entorno `URL_<Ifz>` donde `Ifz` es el nombre de la interfaz en mayúsculas. Por ejemplo, la dirección base del servicio de Trabajos se puede cambiar con:

```sh
URL_TRABAJOS=http://localhost:9000
```

## Despliegue de servicios mediante Docker Compose

En el momento de preparación de esta memoria no se disponía de los desarrollos de los otros equipos por lo que se ha optado por integrar nuestro servidor con "mock-ups" del resto de interfaces, es decir:
- Clientes
- Facturas
- Logs
- Recambios
- Trabajos
- Vehiculos

Cada interfaz consta de dos tipos de contenedores que usan la especificación en OpenAPI publicada por cada uno de los equipos:
- **Front-end**: UI de la interfaz del servicio implementada con SwaggerUI.
- **Back-end**: Mock-up del servicio implementado con Spotlight.

Para el servicio Notificaciones se han definido un contenedor:
- **Back-end**: Servidor de Notificaciones que usa la [imagen][imagen] publicada en DockerHub como se indicó previamente.

Las definiciones de estos contenedores aparecen en el fichero `practica_2/docker-compose.yml` del proyecto y se pueden consultar [aquí][local].

Para validar la integración del servidor de Notificaciones con el resto de servicios podemos ejecutar el siguiente comando `docker compose up -d`dentro de la carpeta `practica_2` del proyecto. Tras ejecutar este comando los servicios de cada contenedor están disponibles en las siguientes direcciones:

| Servicio | Descripción | Dirección |
|----------|----------|----------|
| clientes-frontend | UI de la interfaz Clientes   | [http://localhost:8000](http://localhost:8000)|
| clientes-mock-backend | Mock-up del servicio Clientes   | [http://localhost:4010](http://localhost:4010/clientes)|
| logs-frontend | UI de la interfaz Logs   | [http://localhost:8001](http://localhost:8001)|
| logs-mock-backend | Mock-up del servicio Logs   | [http://localhost:4011](http://localhost:4011/logs)|
| facturas-frontend | UI de la interfaz Facturas   | [http://localhost:8002](http://localhost:8002)|
| facturas-mock-backend | Mock-up del servicio Facturas   | [http://localhost:4012](http://localhost:4012/facturas)|
| notificaciones-backend | Servicio Facturas   | [http://localhost:4013](http://localhost:4013/docs)|
| recambios-frontend | UI de la interfaz Recambios   | [http://localhost:8004](http://localhost:8004)|
| recambios-backend | Mock-up del servicio Recambios   | [http://localhost:4014](http://localhost:4014/recambios)|
| trabajos-frontend | UI de la interfaz Trabajos   | [http://localhost:8005](http://localhost:8005)|
| trabajos-backend | Mock-up del servicio Trabajos   | [http://localhost:4015](http://localhost:4015/trabajos)|
| vehiculos-frontend | UI de la interfaz Vehículos   | [http://localhost:8006](http://localhost:8006)|
| vehiculos-backend | Mock-up del servicio Vehículos   | [http://localhost:4016](http://localhost:4016/vehiculos)|

**NOTA**: FastAPI envía siempre en minúsculas todas las cabeceras de las respuestas HTTP y es posible que las UIs de las interfaces no muestre todas ellas. Se recomienda usar los comandos `curl`con la opción `-i, --include` para confirmar las cabeceras incluidas en la respuesta HTTP.

## Despliegue de servicios con Azure Kubernetes Services (AKS)

Para el despliegue de los servicios en AKS se ha usado la suscripción para estudiantes que ofrece a los estudiantes de la UPM.
La implementación del servicio en AKS implica la realización de las siguientes tareas (para más detalles consultar [aquí][AKS])
- **Creación de un registro de contenedors (ACR)**. El registro se crea con "tier" (o SKU) `Basic` aplicándose los límites de almacenamiento, tamaño de imágenes, ancho de banda, operaciones I/O, etc. que se definen en [Límites SKU][limites-SKU]. Los comandos de Azure Powershell usados han sido (el último comando nos proporciona la dirección para la publicación de imágenes):
```sh
New-AzResourceGroup -Name aos2023notificaciones -Location eastus
New-AzContainerRegistry -ResourceGroupName aos2023notificaciones -Name aos2023notificaciones -Sku Basic
(Get-AzContainerRegistry -ResourceGroupName aos2023notificaciones -Name aos2023notificaciones).LoginServer
```
- **Publicación de la imagen**: Desde la máquina local publicamos la imagen del servicio de Notificaciones en el registro ACR previamente creado. Los comandos usados:
```sh
docker tag acarrasco2000/aos2023-notificaciones:v1 aos2023notificaciones.azurecr.io/azure-aos2023notificaciones:v1
docker push aos2023notificaciones.azurecr.io/azure-aos2023notificaciones:v1
```
- **Creación de un cluster AKS**. El cluster se crea con dos nodos y se asocia al registro ACR anteriormente creado. Se ha usado el comando:
```sh
New-AzAksCluster -ResourceGroupName aos2023notificaciones -Name aos2023notificacionesCluster -NodeCount 2 -AcrNameToAttach aos2023notificaciones
```
Tras estos pasos previos el servicio puede ser desplegado ejecutando el comando `kubectl apply -f .`en la carpeta `kubernetes`. Dicha carpeta contiene los siguientes ficheros kubernetes:
- **Ficheros son el sufijo `-service.yaml`**: Definiciones de los balanceadores de carga que exponen los servicios ejecutados en uno o varios PODs. Existe un fichero por cada servicio y se usan balanceadores de tipo `LoadBalance`, que exponen una dirección IP pública del cluster, y `ClusterIP`, que exponen una dirección IP privada del cluster. Por limitaciones de la suscripción Azure para estudiantes sólo el servicio de Notificaciones usa balanceadores de tipo `LoadBalance` y el resto de servicios usan balanceadores de tipo `ClusterIP`.
- **Ficheros con el sufijo `-deployment.yaml`**: Definiciones de los PODs de los servicios. El número inicial de réplicas es 1 aunque éste pueder ser escalado con los servicios AKS.
- **disco-notificaciones.yaml**: Notificación PVC (Persistent Volume Claim) para un disco de 5GB con clase de almacenamiento `azurefile-csi` (Azure Files)` que es montado por los PODs del servicio de Notificaciones. Este disco se usa para compartir el fichero SQLite con la base de datos del servicio.
- **disco-mockup.yaml**: Notificación PVC (Persistent Volume Claim) para un disco de 1GB con clase de almacenamiento `azurefile-csi` (Azure Files)` que es montado por los mock-ups del resto de servicios. En este disco se guardan las especificaciones en OpenAPI de las interfaces.
- **practica-2-default-networkpolicy.yaml**: Política de red para permitir que los PODs puedan recibir tráfico entrante desde cualquier origen.

Estos los resultados tras ejecutar el comando `kubectl apply -f .` en la carpeta `kubernetes`:

**Creación de los recursos**: comando `kubectl apply -f .`
<img src="../kubernetes/pantallas/Recursos-Creación.png"/>

**Consulta de volúmenes**: comando `kubectl get pvc`
<img src="../kubernetes/pantallas/Disco.png"/>

**Consulta de PODs**: comando `kubectl get pod`
<img src="../kubernetes/pantallas/POD.png"/>

**Consulta de servicios**: comando `kubectl get svc`
<img src="../kubernetes/pantallas/Servicios.png"/>

Podemos observar que el servicio de Notificaciones está escuchando en la dirección `http://40.76.168.63:4013/` que usa dirección IP pública. El portal Azure nos muestra estas cargas de trabajo del cluster AKS:

<img src="../kubernetes/pantallas/Cargas de Trabajo.png"/>

Tras verificar el estado correcto de los recursos creados podemos acceder a la dirección pública de la UI de la interfaz de Notificaciones y cursar una petición GET como aparece en la pantalla:

<img src="../kubernetes/pantallas/UI GET.png"/>

Tamhién podemos aumentar a 2 el número de PODs para el servicio de notificaciones:

<img src="../kubernetes/pantallas/Escalado POD.png"/>

[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)

   [tutorial]: <https://fastapi.tiangolo.com/es/tutorial/sql-databases>
   [ifz]: <https://github.com/OhhTuRnz/AOS_2023_Practica_1/blob/main/openapi/openapi.yaml>
   [imagen]: <https://hub.docker.com/r/acarrasco2000/aos2023-notificaciones/tags>
   [docker]: <https://github.com/OhhTuRnz/AOS_2023_Practica_1/blob/main/Dockerfile>
   [local]: <https://github.com/OhhTuRnz/AOS_2023_Practica_1/blob/main/practica_2/docker-compose.yml>
   [limites-SKU]: <https://learn.microsoft.com/en-us/azure/container-registry/container-registry-skus>
   [AKS]: <https://learn.microsoft.com/es-es/azure/aks/tutorial-kubernetes-prepare-acr?tabs=azure-cl>
   [OAuth 2.0]: <https://oauth.net/2/>