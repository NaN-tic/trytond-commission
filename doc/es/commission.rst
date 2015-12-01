==========
Comisiones
==========

La comisión es la cantidad que se cobra por realizar transacciones comerciales
que corresponden a un porcentaje o un importe fijo sobre el importe de la 
operación.

Las comisiones se calculan sobre las facturas.

.. inheritref:: commission/commission:section:planes

Planes
======

En nuestro sistema deberemos definir que planes se aplicarán para la generación
de comisiones.

Un plan irá relacionado con un producto y el método de comisión. Esto significa 
que siempre deberemos fijarnos que el producto de la línea de venta o factura 
esté contemplado en el plan, con su respectiva fórmula. 

El método de comisión es el estado de la factura en que se creará la comisión:

* Al confirmar
* Al pagar
* Al pagar parcialmente

Los planes irán relacionados con varias líneas. Cada línea la podemos relacionar
con un producto. La comisión se calculará sobre el producto que se facture.
Si aplicamos un plan de comisión a una factura que contiene un producto que no 
esta contemplado en el plan, no se le aplicará la comisión. 

La formula de las líneas de los planes son cálculos matemáticos. Por ejemplo, 
si la comisión es de un 10% del total, el operador será:

.. code::

    amount*0.1

    
Otra condición a tener en cuenta a la hora de generar el plan es el tipo de
producto comisión. Este siempre tendrá que ser tipo servicio, no podrá ser un 
bien.

.. inheritref:: commission/commission:section:agentes

Agentes
=======
 
Los agentes pueden ser los comerciales, empleados por la propia empresa o 
personal externo (autónomos), administradores de comunidades de vecinos o 
gestores, entre otros.

Cada agente irá relacionado con un "plan de comisión". Según el plan de comisión
se le calculará el tipo de comisión que ganará el agente.

El tipo de agente, "agente de" o "principal" nos permite especificar la cuenta 
del agente que
se usará.

Si el agente es "Agente de" se usará la cuenta "Cuenta a pagar" del 
tercero/agente.
Si el agente es "Principal" se usará la cuenta "Cuenta a cobrar" del 
tercero/agente. 

Se nos permitirá modificar la moneda con la cual se paga la comisión al 
comissionista.
Además de poder añadir tantos terceros al Agente, para que se le aplique el 
plan 
de comisiones, como este tenga asignados. De la misma manera, podemos añadir el 
Agente en cualquier ficha de Terceros.

.. inheritref:: commission/commission:section:creacion_comisiones

Creación de comisiones
======================

Las comisiones se crean automáticamente con un plazo en función del tipo de 
plan 
que hayamos definido (al confirmar, al pagar o al pagar parcialmente la 
factura).
Si la factura es de cliente, nos genera comisiones en positivo. Si la factura 
es una devolución de cliente, nos genera las comisiones en negativo.

.. inheritref:: commission/commission:section:relacionar_facturas_con_agentes

Relacionar facturas con agentes
===============================

En la factura disponemos del campo "Agente de comisiones" que nos permite 
relacionar
la factura con el agente y el plan que este tiene asociado.

En el caso que la factura esté relacionada con un agente, en el momento de 
confirmar o pagar
la factura (según el plan) nos genera la comisión seleccionada para el plan 
asociado al agente.

En el caso de que la factura provenga de una venta y tengamos más de una venta 
con diferentes agentes deberemos realizar una factura para cada Agente, si este 
es diferente. 

  **Ejemplo:**

  Una factura provenga de una venta en esta factura disponemos  de diferentes 
  líneas dónde puede que el origen sea de diferentes ventas, y por tanto, de 
  diferentes agentes. En el caso que las líneas de la factura tengan un agente,
  tendrá preferencia este respecto al agente global de la factura o de si no 
  disponemos de agente, las comisiones que se generarán serán respecto a la 
  línea de la factura.

.. inheritref:: commission/commission:section:facturar_comisiones

Facturar las comisiones
=======================

Des del menú de Comisiones disponemos de un asistente que nos permite generar 
facturas a partir
de un rango de fechas.

En este asistente le podemos especificar el tipo de factura:

* *Entrante*. Nos generará facturas de los agentes que el tipo sea "principal".
* *Saliente*. Nos generará facturas de los agentes que el tipo sea "agente de".
* *Ambos*. Nos generará facturas de los agentes que sean "principal" y "agente 
  de".

Para generar las facturas de la comisión es importante que los agentes 
dispongan 
de un "plazo de pago" tanto de cliente como proveedor por defecto antes de 
ejecutar el asistente.
En el caso que el agente no disponga de esta información, una mensaje de alerta 
nos avisará que no puede generar la factura, pues este campo es requerido en la 
factura.

.. inheritref:: commission/commission:section:cancelar_facturas

Cancelar facturas relacionadas con comisiones
=============================================

En el caso que se cancele una factura con líneas pertenecientes a comisiones ya 
facturadas, estas comisiones pasarán a estado "cancelado". Un ejemplo seria una 
factura de cliente que genera comisiones, generamos la factura de las 
comisiones 
(factura de proveedor) y la cancelamos. Al cancelarla automáticamente las 
comisiones pasarán a estado "cancelado"