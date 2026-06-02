# Arquitectura

La solucion separa la interpretacion conversacional de la logica comercial. El LLM local se usa para entender mensajes de clientes y extraer entidades, mientras que la API decide que productos existen, que precio tienen, donde estan disponibles y cuantas unidades hay.

## Componentes

- **FastAPI:** expone `/productos`, `/disponibilidad` y `/leads`.
- **SQLite:** almacena catalogo estructurado y leads.
- **Seed de catalogo:** transforma el texto de la prueba en datos validados. Puede intentar LM Studio con `--use-llm`, pero conserva un catalogo validado para reproducibilidad.
- **n8n:** orquesta mensajes, llamadas al LLM local y llamadas a la API.
- **LM Studio:** proveedor local compatible con OpenAI, configurado con `meta-llama-3.1-8b-instruct`.

## Limites De La IA

La IA no puede inventar precios, stock, ubicaciones ni compatibilidades. Si un producto no aparece en la API, el bot debe decir que no lo encontro y registrar la solicitud para seguimiento humano.

La compatibilidad se expresa como general porque el texto fuente no contiene anio, version ni motor exacto para todos los productos. Cuando el cliente pide confirmacion definitiva, el flujo marca el caso para asesor.

## Escalabilidad

Con 10,000 productos convendria migrar a PostgreSQL, agregar indices por marca/modelo/categoria/ciudad y probablemente busqueda semantica o full-text search. La API y n8n podrian mantenerse, pero la busqueda simple `LIKE` deberia reemplazarse por un motor mas robusto.
