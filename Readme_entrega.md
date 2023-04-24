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

> Nunca useis el tag latest de cualquier imagen porque si sacan
> una nueva versión sin retrocompatibilidad la has cagado.
