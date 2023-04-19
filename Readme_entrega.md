# Entrega de la práctica AOS-2023 por el Equipo 5
## Especificación de una api utilizando openapi y su despliegue con docker.

Estos son los pasos para poder acceder a la especificación:

- git clone git@github.com:OhhTuRnz/AOS_2023_Practica_1.git
- cd AOS\_2023\_Practica_1/
- docker-compose up o docker compose up dependiendo de tu versión de docker.
- Observar como se han lanzado los contenedores aos2023\_notificaciones\_mock, aos2023\_notificaciones\_ui y aos2023\_notificaciones\_proxy.
- ✨  Tenemos disponible nuestra especificación (localhost:8000 o 127.0.0.1:8000)  ✨ 

## Decisiones de diseño

- Vemos importante utilizar el id de trabajo como un objeto dentro de nuestra api porque será de la que dependa la notificación, y de dónde se podrá encontrar el VIN y el cliente.
- Una notificación no debería ser modificada bajo ninguna circunstancia porque podría generar problemas de experiencia del usuario y gestión, por lo que no vemos conveniente incluir un PUT en ningún endpoint.
- Esta api podrá ser utilizada por clientes o gestiones de otros talleres, por lo que dejar abierto un endpoint delete pondría en riesgo el sistema, y la eliminación de notificaciones *viejas* o *inútiles* sería capacidad del sistema o servidor.
- Para facilitación de trabajos, existirá un endpoint de trabajo para encontrar las notificaciones, con una alternativa para la API de trabajo comentada más abajo, es importante recalcar que sólo tendrá un c_get de las notificaciones de un trabajo.
- Existe un error peculiar, *409 Conflict*, ya que puede existir un conflicto con los datos que se añaden en el servidor si, por ejemplo, pasamos de un estado Creado a uno Finalizado sin pasar antes por Iniciado, o crear una notificación por primera vez de un trabajo sin el estado por defecto *Creado*.

Siguiendo las recomendaciones de Alberto Díaz:

> Nunca useis el tag latest de cualquier imagen porque si sacan
> una nueva versión sin retrocompatibilidad la has cagado.
