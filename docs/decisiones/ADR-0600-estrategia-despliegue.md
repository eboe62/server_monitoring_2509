# ADR-0600: Estrategia de Despliegue: Arquitectura de Microservicios Independientes basados en Maven Multi-Module

## Estado
ACCEPTED

## Contexto
El backend de la plataforma GDA está compuesto por múltiples carpetas de negocio diferenciadas (gda-finance, gda-imputacion, gda-persona, etc.). Cada una cuenta de forma nativa con su propio wrapper de Maven (`mvnw`), su directorio de configuración `.mvn` y su archivo `pom.xml` independiente. Esto demuestra que, aunque comparten el mismo repositorio de código (Monorrepo), no están concebidos como un único monolito acoplado en tiempo de compilación.

## Decisión
Establecer un modelo de arquitectura de Microservicios Desacoplados. Cada módulo se tratará como un artefacto con ciclo de vida, compilación y despliegue completamente independiente. Se prohíbe la creación de un `pom.xml` padre en la raíz que fuerce una compilación en bloque reactiva si no es estrictamente necesario para la canalización de CI/CD.

## Consecuencias

### Positivas (+)
- Permite desplegar cambios en un módulo (ej. `gda-finance`) sin necesidad de recompilar, probar o reiniciar los demás módulos (ej. `gda-persona`).
- Escalabilidad horizontal independiente por cada servicio según la carga de trabajo.

### Negativas (-)
- Exige una gestión rigurosa de las versiones de las dependencias de forma externa (o mediante un BOM compartido) para evitar la deriva tecnológica entre servicios.
