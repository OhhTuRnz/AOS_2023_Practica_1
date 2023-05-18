FROM stoplight/prism:4

COPY ./especificaciones /app/mockup/especificaciones

EXPOSE 4010
EXPOSE 4011
EXPOSE 4012
EXPOSE 4013
EXPOSE 4014
EXPOSE 4015

WORKDIR /usr/src/prism/packages/cli

CMD ["mock", "--cors", "-h", "0.0.0.0", "-p", "4010", "/app/mockup/especificaciones/clientes/openapi.yaml]
CMD ["mock", "--cors", "-h", "0.0.0.0", "-p", "4011", "/app/server/especificaciones/facturas/openapi.yaml]
CMD ["mock", "--cors", "-h", "0.0.0.0", "-p", "4012", "/app/server/especificaciones/notificaciones/openapi.yaml]
CMD ["mock", "--cors", "-h", "0.0.0.0", "-p", "4013", "/app/server/especificaciones/recambios/openapi.yaml]
CMD ["mock", "--cors", "-h", "0.0.0.0", "-p", "4014", "/app/server/especificaciones/trabajos/openapi.yaml]
CMD ["mock", "--cors", "-h", "0.0.0.0", "-p", "4015", "/app/server/especificaciones/vehiculos/openapi.yaml]
