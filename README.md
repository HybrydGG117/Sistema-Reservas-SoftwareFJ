# Sistema Integral de Gestión de Clientes, Servicios y Reservas - Software FJ

Proyecto desarrollado para el curso **Programación (Código: 213023)** de la **Universidad Nacional Abierta y a Distancia (UNAD) - ECBTI**.

## Descripción del Proyecto
Aplicación orientada a objetos desarrollada en Python que gestiona clientes, servicios tecnológicos (reservas de salas, alquiler de equipos y asesorías especializadas) y reservas en memoria, sin uso de bases de datos, aplicando manejo avanzado de excepciones y registro de auditoría en archivo de logs.

## Principios de POO y Requisitos Implementados
- **Abstracción:** Clases abstractas `EntidadSistema` y `Servicio` utilizando el módulo `abc`.
- **Encapsulación:** Atributos privados y validaciones estrictas mediante `@property` en la clase `Cliente`.
- **Herencia y Polimorfismo:** Tres clases especializadas (`ReservaSala`, `AlquilerEquipo`, `AsesoriaEspecializada`) que sobrescriben `validar_parametros()`, `calcular_costo()` y `describir_servicio()`.
- **Sobrecarga de Métodos:** Método `calcular_total_facturacion()` con parámetros opcionales para aplicar descuentos e IVA dinámicamente.
- **Manejo Avanzado de Excepciones:** Excepciones personalizadas (`ErrorSistemaFJ`, `DatoInvalidoError`, `ServicioNoDisponibleError`, `ReservaInvalidaError`), uso de bloques `try/except/else/finally` y encadenamiento de excepciones (`raise ... from ...`).
- **Logs en Archivo:** Registro automático de eventos y errores en `registro_eventos.log`.

## Ejecución
1. Asegúrese de tener **Python 3.10+** instalado.
2. Ejecute en la terminal:
   python sistema_software_fj.py
3. Verifique la salida en consola y el archivo generado `registro_eventos.log`.
