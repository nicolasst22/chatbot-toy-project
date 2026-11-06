---
titulo: Stock, reservas y productos alternativos
tipo_doc: politica
tema: stock
---

# Stock, reservas y productos alternativos

## Cómo se informa el stock

El stock es en tiempo real y sale de la columna `stock` de la tabla `productos`.

- **stock = 0:** sin stock. Si `fecha_reposicion` tiene un valor, es la fecha estimada de ingreso; si está vacía, no hay fecha confirmada y no hay que prometer ninguna.
- **stock entre 1 y 3:** últimas unidades. Conviene avisarle al cliente que puede agotarse.
- **stock de 4 o más:** disponible.

El asistente no debe decir el número exacto de unidades si es mayor a 10; alcanza con "hay stock disponible".

## Qué hacer cuando un producto no tiene stock

1. Avisar que no hay stock y, si existe, la fecha estimada de reposición.
2. Ofrecer alternativas con la tabla `equivalencias` (o la vista `v_alternativas_con_stock`), que ya filtra las que sí tienen stock. Las alternativas están ordenadas por `ranking`: 1 es la más parecida.
3. Explicar en una línea por qué la alternativa es equivalente, usando la columna `motivo` (por ejemplo, "mismo chip RTX 5070" o "mismo socket AM5 y DDR5").
4. Si el producto forma parte de un armado de PC, validar la compatibilidad de la alternativa con el resto de los componentes antes de ofrecerla. Las equivalencias respetan el socket y el tipo de memoria, pero no conocen el resto del armado del cliente.
5. Ofrecer el aviso de reposición: el cliente deja su email y le escribimos cuando ingresa.

Una alternativa más cara se ofrece solo si no hay una de precio similar, y siempre aclarando la diferencia.

## Reservas

Un producto con stock se puede reservar 48 horas pagando una seña del 20 %. La seña congela el precio en dólares. Si el cliente no completa la compra en ese plazo, la seña queda como saldo a favor por 6 meses.

Los productos sin stock con fecha de reposición confirmada se pueden reservar con una seña del 30 %. Si la mercadería no llega dentro de los 15 días posteriores a la fecha informada, el cliente puede pedir el reintegro completo de la seña.

## Límite por cliente

En placas de video de gama alta (RTX 5080, RTX 5090, RX 9070 XT) y en lanzamientos de Apple, el máximo es de 2 unidades por cliente.
