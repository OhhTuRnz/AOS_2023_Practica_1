#!/bin/bash
read -p "Dime el directorio de entrega: " dir

if [ "$dir" != "" ]
then
    read -p "El directorio es $dir. Pulsa [S] si deseas continuar: " confirma
    if [ "$confirma" == "S" ]
    then
       mkdir -p nuevo
       b=`echo $dir | sed 's/\//\\\\\//g'`
       for i in `ls *yaml`
       do
          echo "Procesando $i"
          cat $i | sed "s/\/home\/azureuser\/AOS\/Entrega/$b/" > nuevo/$i
       done 
       echo
       echo "Los ficheros *yaml creados se encuentran en el subdirectorio nuevo"
    fi
fi
