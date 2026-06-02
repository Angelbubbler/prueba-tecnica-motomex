# Evidencia de Conversaciones

Pruebas ejecutadas contra:

- **API:** `http://127.0.0.1:8000`
- **n8n webhook:** `POST http://localhost:5678/webhook/motomex-chatbot`
- **Workflow activo:** `7f4adf6e-4b3f-4a4e-81f8-3f4bb3d6f8e2`
- **Sesión final validada:** `final-carlos-v3`

---

## Caso 1: Búsqueda General

**Cliente:**
```text
Hola, busco una batería para un Versa.
```

**Respuesta del Bot:**
```text
Claro. Tenemos Batería automotriz LTH L-47-650 que puede ser compatible de forma general con Nissan Versa, Chevrolet Aveo, Volkswagen Jetta. Para validar mejor, ¿me puedes compartir el año de tu vehículo, ciudad y estado?
```

* **Lead registrado:** Estado **incompleto**, almacenando `producto_interes = Bateria automotriz LTH L-47-650` y `vehiculo = Nissan Versa`.

---

## Caso 2: Cliente da Datos

**Cliente:**
```text
Soy Carlos, estoy en Monterrey, Nuevo León. Mi Versa es 2020.
```

**Respuesta del Bot:**
```text
Gracias, Carlos. Batería automotriz LTH L-47-650 está disponible en Monterrey, Nuevo León, con 8 unidades en stock y tiene un precio de $2,450 MXN. ¿Deseas continuar con la compra o prefieres que un asesor revise primero la compatibilidad?
```

* **Lead registrado:** El mismo lead de la sesión se actualiza guardando el nombre (*Carlos*), ciudad (*Monterrey*), estado (*Nuevo León*) y el año del vehículo (*2020*). El estado del lead sigue siendo **incompleto** hasta que se confirme la compra y se proporcione la dirección de envío.

---

## Caso 3: Cliente Quiere Comprar (Cierre de Venta)

**Cliente:**
```text
Sí, quiero comprar la batería LTH L-47-650. Mi dirección es Av. Universidad 123, Colonia Centro, Monterrey, Nuevo León, C.P. 64000.
```

**Respuesta del Bot:**
```text
Gracias. Registré tu solicitud de compra y la dirección de envío. Un asesor puede validar la compatibilidad final antes de surtir el pedido.
```

* **Lead final registrado en base de datos:**
```json
{
  "session_id": "final-carlos-v3",
  "nombre": "Carlos",
  "ciudad": "Monterrey",
  "estado": "Nuevo León",
  "producto_interes": "Batería automotriz LTH L-47-650",
  "vehiculo": "Nissan Versa",
  "anio_vehiculo": "2020",
  "direccion_envio": "Av. Universidad 123, Colonia Centro, Monterrey, Nuevo León, C.P. 64000.",
  "lead_completo": true
}
```

---

## Caso 4: Producto Ambiguo

**Cliente:**
```text
Necesito unas balatas.
```

**Respuesta del Bot:**
```text
Claro. Para ayudarte mejor, ¿me puedes compartir el modelo, año de tu vehículo y la ciudad donde te encuentras?
```

* **Lead registrado:** Estado **incompleto**, identificando como producto de interés *Balatas delanteras Bosch BP-1290*, pero con los datos del vehículo y ubicación marcados como pendientes para evitar suposiciones incorrectas.

---

## Caso 5: Producto Fuera de Catálogo

**Cliente:**
```text
¿Tienen filtro de aceite para March?
```

**Respuesta del Bot:**
```text
Por ahora no encontré filtro de aceite para Nissan March en el catálogo disponible. Puedo registrar tu solicitud para que un asesor la revise. ¿Me compartes tu nombre, ciudad y estado?
```

* **Lead registrado:** Estado **incompleto**, identificando que el producto de interés es un *filtro de aceite* para *Nissan March*, y solicitando los datos personales y de ubicación del cliente para que un vendedor le dé seguimiento de forma offline.
