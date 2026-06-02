# Evidencia De Conversaciones

Pruebas ejecutadas contra:

- API: `http://127.0.0.1:8000`
- n8n webhook: `POST http://localhost:5678/webhook/motomex-chatbot`
- Workflow activo: `7f4adf6e-4b3f-4a4e-81f8-3f4bb3d6f8e2`
- Sesion final validada: `final-carlos-v3`

## Caso 1: Busqueda General

Cliente:

```text
Hola, busco una bateria para un Versa.
```

Respuesta:

```text
Claro. Tenemos Bateria automotriz LTH L-47-650 que puede ser compatible de forma general con Nissan Versa, Chevrolet Aveo, Volkswagen Jetta. Para validar mejor, me puedes compartir anio del vehiculo, ciudad y estado?
```

Lead registrado: incompleto, con `producto_interes = Bateria automotriz LTH L-47-650` y `vehiculo = Nissan Versa`.

## Caso 2: Cliente Da Datos

Cliente:

```text
Soy Carlos, estoy en Monterrey, Nuevo Leon. Mi Versa es 2020.
```

Respuesta:

```text
Gracias, Carlos. Bateria automotriz LTH L-47-650 esta disponible en Monterrey, Nuevo Leon, con 8 unidades en stock y tiene un precio de $2,450 MXN. Deseas continuar con la compra o prefieres que un asesor revise primero compatibilidad?
```

El mismo lead se actualiza con nombre, ciudad, estado y anio del vehiculo.

## Caso 3: Cliente Quiere Comprar

Cliente:

```text
Si, quiero comprar la bateria LTH L-47-650. Mi direccion es Av. Universidad 123, Colonia Centro, Monterrey, Nuevo Leon, C.P. 64000.
```

Respuesta:

```text
Gracias. Registre tu solicitud de compra y la direccion de envio. Un asesor puede validar compatibilidad final antes de surtir el pedido.
```

Lead final:

```json
{
  "session_id": "final-carlos-v3",
  "nombre": "Carlos",
  "ciudad": "Monterrey",
  "estado": "Nuevo Leon",
  "producto_interes": "Bateria automotriz LTH L-47-650",
  "vehiculo": "Nissan Versa",
  "anio_vehiculo": "2020",
  "direccion_envio": "Av. Universidad 123, Colonia Centro, Monterrey, Nuevo Leon, C.P. 64000.",
  "lead_completo": true
}
```

## Caso 4: Producto Ambiguo

Cliente:

```text
Necesito unas balatas.
```

Respuesta:

```text
Claro. Para ayudarte mejor, me puedes compartir el modelo, anio de tu vehiculo y la ciudad donde te encuentras?
```

## Caso 5: Producto Fuera De Catalogo

Cliente:

```text
Tienen filtro de aceite para March?
```

Respuesta:

```text
Por ahora no encontre filtro de aceite para Nissan March en el catalogo disponible. Puedo registrar tu solicitud para que un asesor la revise. Me compartes tu nombre, ciudad y estado?
```
