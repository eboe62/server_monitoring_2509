# ADR-0603: Políticas de Gestión de Bases de Datos en Microservicios

Status: APPROVED
Date: 2026-06-11
Decision Type: REVIEW_REQUIRED
Scope: Database
Tags: REVIEW_REQUIRED
Related ADRs: ADR-0600
Supersedes: NONE
Superseded By: NONE
Validation Reference: NONE

## Contexto
En una arquitectura de microservicios desacoplados, cada servicio debe ser independiente en todos los aspectos, incluida la gestión de datos. Actualmente, no se han definido lineamientos claros sobre cómo los microservicios deben gestionar sus bases de datos, lo que puede llevar a conflictos de acceso, acoplamiento entre servicios y dificultades para escalar.

## Decisión
Adoptar el patrón de "Base de datos por Microservicio" con las siguientes directrices:
1. **Independencia:** Cada microservicio tendrá su propia base de datos, gestionada de forma independiente.
2. **Prohibición de Joins:** No se permitirán uniones (joins) entre bases de datos de distintos servicios. La integración de datos deberá realizarse a través de APIs.
3. **Migraciones de Esquema:** Cada servicio será responsable de gestionar sus propias migraciones de esquema utilizando herramientas como Flyway o Liquibase.
4. **Segregación de Datos:** En entornos compartidos, se utilizarán esquemas o instancias separadas para cada servicio.

## Consecuencias

### Positivas (+)
- Garantiza el desacoplamiento total entre servicios.
- Facilita la escalabilidad y el mantenimiento de cada servicio de forma independiente.
- Reduce el riesgo de conflictos en el acceso a datos.

### Negativas (-)
- Introduce complejidad adicional en la gestión de múltiples bases de datos.
- Requiere un esfuerzo adicional para implementar integraciones entre servicios.
