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
### <sub>Subsistema_4: Envío de notificaciones relacionadas con el funcionamiento del taller.</sub>
Este subsistema es el encargado de notificar a los clientes las modificaciones de cambio de estado de los diferentes trabajos.
### Subsistema_5: Gestión y emisión de facturas a los clientes por los trabajos realizados.
Una vez terminados todos los trabajos solicitados por un cliente, este subsistema creará la factura correspondiente.
### Subsistema_6: Gestión del inventario completo de recambios del taller (incluirá nombre, descripción, proveedor, equivalencias, etc.)
### Subsistema_7: Gestión de los logs del resto de subsistemas.
Permitirá registrar eventos que quedarán almacenados para su posterior consulta, generación de informes, estadísticas, etc. Es importante identificar de alguna manera el subsistema que registra el evento, la fecha, algún tipo de mensaje descriptivo, prioridad, etc
Para cada uno de los puntos anteriores se deberá especificar el conjunto de operaciones disponibles. Para publicar la especificación se deberá generar un conjunto de contenedores Docker que ofrezcan la definición de las operaciones disponibles en el servicio y describan las conexiones con otros servicios. Todos los subsistemas emitirán un log cuando realicen cualquiera de las operaciones ofrecidas.
