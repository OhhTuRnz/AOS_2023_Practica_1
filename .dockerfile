FROM ubuntu:latest
LABEL autor='Grupo_5_AOS'
ENV xhttp_proxy http://user:pass@proxy/
ENV xhttps_proxy http://user:pass@proxy/
RUN apt-get update
EXPOSE 80