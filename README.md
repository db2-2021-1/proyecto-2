# Proyecto 2

## Dependencias

### Python
- `Django`
- `nltk`

Go to the directory root and run:
`pip install -r requirements.txt`

## Construcción
Los archivos json son parseados y sus arreglos iterados.
De cada objeto se obtiene el `id` y `text`.
El `id` es usado como el nombre del documento y `text` como su contenido.

Usando `python-nltk` el `text` es tokenizado, `stem()`eado, convertido a minúscula
y filtrado.

A partir del vector de palabras obtenido, el índice es actualizado con el nuevo `id`
y las frecuencias de sus palabras.

## Memoria secundaria
El índice puede ser guardado en la memoria secundaría con `dump()` y cargado con `load()`.

## Ejecución de consultas
El texto de la consulta es procesado de la misma manera que el texto de los tweets.
Para el query y los documentos que contienen al menos una palabra de la consulta,
los vectores tf_idf son creados.

A cada documento se le asigna un valor que corresponde a la distancia de coseno con
el vector del query.

Al final los documentos son ordenados por la distancia.
