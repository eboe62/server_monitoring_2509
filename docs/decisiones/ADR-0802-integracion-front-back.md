# ADR-0802: Lineamientos de Integración Frontend con Microservicios Backend

## Estado
Proposed

## Contexto
El frontend del proyecto debe interactuar con múltiples microservicios backend, lo que introduce desafíos en la gestión de llamadas, manejo de errores y consistencia en la comunicación. Actualmente, no se han definido lineamientos claros para esta integración, lo que puede generar inconsistencias y dificultades en el desarrollo.

## Decisión
Adoptar los siguientes lineamientos para la integración del frontend con los microservicios backend:
1. **Uso de API Gateway:** Todas las llamadas del frontend a los microservicios pasarán a través de un API Gateway para centralizar la gestión de rutas y seguridad.
2. **CORS Configurado:** Configurar CORS en el API Gateway para permitir el acceso desde el frontend.
3. **Manejo de Errores:** Implementar un sistema centralizado de manejo de errores en el frontend para gestionar respuestas de los microservicios.
4. **Clientes HTTP:** Utilizar una librería estándar (ej. Axios) para realizar las llamadas HTTP desde el frontend.

## Consecuencias

### Positivas (+)
- Centraliza la gestión de rutas y seguridad en el API Gateway.
- Mejora la consistencia en la comunicación entre el frontend y el backend.
- Facilita el manejo de errores y la depuración.

### Negativas (-)
- Introduce una dependencia adicional en el API Gateway.
- Requiere un esfuerzo inicial para configurar CORS y manejar errores de forma centralizada.
