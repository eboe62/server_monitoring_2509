# ADR-0803: Estrategias de Seguridad y Gestión de Secretos en Microservicios

## Estado
Proposed

## Contexto
En un ecosistema de microservicios, la seguridad y la gestión de secretos son fundamentales para proteger datos sensibles y garantizar la confiabilidad del sistema. Actualmente, no se han definido lineamientos claros sobre cómo manejar variables de entorno, secretos y autenticación entre servicios.

## Decisión
Adoptar las siguientes estrategias de seguridad y gestión de secretos:
1. **Variables de Entorno Seguras:** Utilizar archivos `.env` para gestionar configuraciones sensibles en entornos locales y bóvedas de secretos (ej. HashiCorp Vault) en producción.
2. **Autenticación Stateless:** Implementar autenticación basada en tokens JWT para garantizar sesiones seguras y escalables.
3. **Rotación de Secretos:** Establecer políticas de rotación periódica de secretos para minimizar riesgos.
4. **Cifrado de Datos Sensibles:** Asegurar que todos los datos sensibles almacenados estén cifrados tanto en tránsito como en reposo.

## Consecuencias

### Positivas (+)
- Mejora la seguridad del sistema al proteger datos sensibles.
- Facilita la escalabilidad mediante autenticación stateless.
- Reduce el riesgo de exposición de secretos mediante bóvedas seguras.

### Negativas (-)
- Introduce complejidad adicional en la configuración y gestión de secretos.
- Requiere capacitación para los desarrolladores sobre el uso de bóvedas y autenticación JWT.
