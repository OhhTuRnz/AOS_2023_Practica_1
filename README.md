# AOS_2023_Practica_1
## Rúbrica
![image](https://user-images.githubusercontent.com/72455516/225698324-2b407d28-63b3-4732-b0f6-d438037fe033.png)
## Objetivo:
El principal objetivo de esta tarea consiste en consolidar los conceptos relacionados con el diseño y la especificación de un servicio. Para ello se definirá y publicará la definición de un servicio empleando el estándar OpenAPI 3. Adicionalmente se simulará el comportamiento del servicio (se propone el empleo de Swagger-UI, Stoplight Prism, Postman, ...)

## Enunciado:

Para conseguir este objetivo se van a definir un conjunto de servicios que, posteriormente, se emplearán para desarrollar una aplicación de gestión de talleres de mecánica rápida. En primer lugar se formarán equipos de como máximo cinco alumnos, y cada equipo deberá realizar la especificación de uno de los servicios propuestos.

Sistema de Gestión de talleres de mecánica rápida
Una conocida empresa que posee talleres de mecánica rápida por toda la geografía nacional nos ha encargado la realización de un sistema de gestión para una parte de su negocio. A efectos de funcionalidad, cada uno de los talleres se gestiona de forma independiente, por lo que cada uno de ellos tendrá su propio despliegue de la aplicación.

Tras una primera reunión con el cliente, nuestro ingeniero de requisitos ha sido capaz de capturar la funcionalidad deseada para el sistema, que se detallan en los siguientes subsistemas:


### Subsistema_1: Gestión de clientes 
Este subsistema se encargará de las operaciones relacionadas con la gestión integral de clientes del taller. Proporcionará operaciones que permitan dar de alta, modificar y buscar clientes (por diferentes criterios) para el resto del sistema. Cada cliente dispondrá de un identificador único de Cliente que será inmutable.
### Subsistema_2: Gestión de los vehículos que son propiedad de los clientes y que se reparan y/o revisan en el taller.
Cada vehículo estará identificado de forma única por su VIN.
### Subsistema_3: Gestión de la planificación diaria de los trabajos del taller, es decir, una colección de trabajos de mantenimiento que se deben realizar sobre determinados vehículos.
Una vez creado un trabajo, los posibles estados serán (al menos): creado, planificado, iniciado y terminado.
### (NUESTRO) Subsistema_4: Envío de notificaciones relacionadas con el funcionamiento del taller.
Este subsistema es el encargado de notificar a los clientes las modificaciones de cambio de estado de los diferentes trabajos.
### Subsistema_5: Gestión y emisión de facturas a los clientes por los trabajos realizados.
Una vez terminados todos los trabajos solicitados por un cliente, este subsistema creará la factura correspondiente.
### Subsistema_6: Gestión del inventario completo de recambios del taller (incluirá nombre, descripción, proveedor, equivalencias, etc.)
### Subsistema_7: Gestión de los logs del resto de subsistemas.
Permitirá registrar eventos que quedarán almacenados para su posterior consulta, generación de informes, estadísticas, etc. Es importante identificar de alguna manera el subsistema que registra el evento, la fecha, algún tipo de mensaje descriptivo, prioridad, etc
Para cada uno de los puntos anteriores se deberá especificar el conjunto de operaciones disponibles. Para publicar la especificación se deberá generar un conjunto de contenedores Docker que ofrezcan la definición de las operaciones disponibles en el servicio y describan las conexiones con otros servicios. Todos los subsistemas emitirán un log cuando realicen cualquiera de las operaciones ofrecidas.

# Entrega Práctica 1 - Equipo 5 - Subsistema de notificaciones - AOS 2023
## Especificación de una api utilizando OpenAPI y su despliegue con docker.

### Pasos para acceder a la especificación:

Para acceder al repositiorio, este se podrá clonar mediante el siguiente comando:

     git clone git@github.com:OhhTuRnz/AOS_2023_Practica_1.git
     
Una vez clonado, ejecutaremos el siguiente comando en la terminal

    cd AOS_2023_Practica_1/

En la terminal introducir el siguiente comando:

     docker-compose up 
     
O bien:

    docker compose up
    
Dependiendo de la versión de Docker que estés ejecutando.

Una vez introducido, observar como se lanzan los contenedores *aos2023\_notificaciones\_mock, aos2023\_notificaciones\_ui y aos2023\_notificaciones\_proxy.*

La especificación está disponible en **localhost:8000** o **127.0.0.1:8000.**


### Decisiones de diseño

- Dentro de nuestra API es importante utilizar el ID de un trabajo como un objeto de nuestra API, ya que una notificación depende de estos. Además a través de su ID podemos encontrar el VIN del vehículo y el cliente para el que se está realizando el trabajo. 
- Una notificación no debería ser modificada bajo ninguna circunstancia porque podría generar problemas de experiencia del usuario y gestión, por lo que no vemos conveniente incluir un PUT en ningún endpoint. Cabe destacar que en caso de que una notificación se enviase de manera incorrecta se podrá eliminar, motivo por el que se ha incluido un *DELETE* a través del id de la notificación.
- Para facilitación de trabajos, existirá un endpoint de trabajo para encontrar las notificaciones, con una alternativa para la API de trabajo comentada más abajo, es importante recalcar que sólo tendrá un c_get de las notificaciones de un trabajo.
- Existe un error peculiar, *409 Conflict*, ya que puede existir un conflicto con los datos que se añaden en el servidor. En nuestro caso ocurre cuando al  crear una notificación por primera vez de un trabajo sin el estado por defecto *Creado*.
- Siguiendo las recomendaciones de Alberto Díaz no se utiliza el tag latest en las imágenes de Docker porque en caso de que se lance una nueva versión de alguna imagen sin retrocompatibilidad podemos tener problemas a la hora de desplegar la especificación.
- Tener en cuenta, también, que el endpoint donde se agrupan las notificaciones por trabajo correspondería canónicamente a la API dedicada a trabajos, pero como esta primera entrega no permite coordinación con el resto de las APIs se codifica en esta misma pudiéndose trasladar a la de trabajos en un futuro.
- Al no tener tantas notificaciones un trabajo, no vemos necesaria la paginación como sí vemos en el cget de todas las notificaciones.
- Como en el repositorio de F. Javier, hemos añadido un documento http para probar la conexión con un cliente REST a la api desplegada.
- El único valor que necesitamos indicar en un post para notificación es el id de trabajo, esto se debe a que el id se generará automáticamente en base al trabajo, el estado tiene un valor por defecto (Creado) y la fecha la calculará el sistema, se podrá añadir opcionalmente estado y detalle.

Como diría Alberto:
> Nunca useis el tag latest de cualquier imagen porque si sacan
> una nueva versión sin retrocompatibilidad la has cagado.
