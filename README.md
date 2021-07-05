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

## Ejecución de consultas
