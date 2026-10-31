# ADR-0608: Estrategia de Almacenamiento de Adjuntos de Noticia (Espacio Justicia)

Status: APPROVED

Date: 2026-08-14 (nota de actualización 2026-08-20 — módulo propietario cambiado, ver ADR-0609)

Scope:
System

Category:
INFRASTRUCTURE

Tags:
REVIEW_REQUIRED

Related ADRs:
[ADR-0607, ADR-0603]

Supersedes:
NONE

Superseded By:
NONE

---

## Contexto

El módulo de Noticias de `gda-comunicacion` (ADR-0607) necesita almacenar adjuntos binarios (imágenes, documentos, vídeos) asociados a cada noticia — una capacidad que no existe en ningún otro microservicio del backend GDA: los 8 módulos existentes gestionan exclusivamente datos relacionales, ninguno persiste ficheros.

La decisión ya se había anticipado como pendiente en la sesión de diseño original (2026-07-22, `Documentacion_BackEnd_EspacioJusticia_2607.md`), que dejó explícitamente anotado: *"ADR propuesto pendiente (ADR-0605): Estrategia de almacenamiento de objetos para adjuntos de contenido — decisión-hija derivada de este ADR"*. Ese número (`ADR-0605`) se asignó después a una decisión distinta ya aprobada (modelo de autorización RBAC), dejando la decisión de almacenamiento sin formalizar — la misma laguna de gobernanza que motivó ADR-0607 para la topología del microservicio.

A diferencia de julio, esta vez la decisión se formaliza con **implementación real verificada**, no como plan: el requisito funcional (`requisitos02.2.md`, apartado GESTOR DOCUMENTAL) ya fijaba la convención de carpetas y nombres de fichero, apuntando a una ruta (`/data/espacio-justicia/…`) que **resultó no existir** en el servidor real (`ineco.ietreir01sdes`, `172.16.22.114`) — corregida el mismo día (2026-08-14) tras inspeccionar el servidor: la raíz real es `/gda/`, junto al resto de infraestructura del proyecto (`/gda/REIR_GDACT`, `/gda/gitlab`).

## Decisión

Se adopta almacenamiento en **filesystem propio del servidor**, no un object storage dedicado (S3/MinIO u otro) — no existe esa infraestructura en el proyecto GDA hoy, y no se introduce solo para este módulo.

1. **Raíz de almacenamiento:** `/gda/espacio-justicia/noticias` en los servidores reales (`dev`/`pre`/`pro`), creada y verificada con permisos (`ineco:ineco`) en desarrollo. Configurable vía `gda-comunicacion.storage.base-path` (`application-{dev,pre,pro}.yml`), nunca hardcodeada en el código — `NoticiaAdjuntoStorageServiceImpl` la lee por `@Value`.
2. **Perfil `local` con ruta distinta y deliberadamente separada:** una máquina de desarrollo Windows no tiene `/gda` montado, así que `application-local.yml` usa una ruta relativa (`./storage-local/espacio-justicia/noticias`), excluida de Git. Es la primera vez que `local` diverge de `dev` en una propiedad de infraestructura en este backend (hasta ahora siempre apuntaban a los mismos valores) — divergencia justificada porque, a diferencia del datasource (que sí puede compartirse contra el servidor remoto), un filesystem local no puede.
3. **Convención de carpetas y nombres**, ya fijada en el requisito funcional y implementada tal cual: `{base-path}/{año}/{noticiaId}/{imagenes|documentos}/{noticiaId}_{prefijo}_{NN}.{ext}`, con `{prefijo}` = `img` (IMAGEN), `doc` (DOCUMENTO) o `vid` (VIDEO) — los vídeos comparten la subcarpeta `documentos/` con los documentos (la convención original solo definía dos subcarpetas; no se crea una tercera para vídeo). `{NN}` es un contador por noticia y subcarpeta, calculado en el momento de subida (`NoticiaAdjuntoRepository.countByNoticiaIdAndTipoIn`).
4. **BBDD guarda solo metadatos y ruta relativa** (`noticia_adjunto.ruta_relativa`), nunca la ruta absoluta — permite mover la raíz de almacenamiento sin migrar datos.
5. **Descarga en streaming desde el propio microservicio**, no servida directamente por un servidor web estático ni por el Gateway — necesario para poder aplicar autorización (ADR-0605) antes de entregar el binario.
6. **Sin límites duros de tamaño aplicados por el servidor**, conforme al requisito funcional explícito ("no podemos limitar o restringir el tamaño de los archivos") — los tamaños máximos por tipo (imagen 3 MB, PDF 10 MB, PPTX 30 MB, hoja de cálculo 5 MB, vídeo 300 MB) son orientativos, solo para dimensionar infraestructura.

## Alternativas Consideradas

**A — Object storage dedicado (S3/MinIO).** Más escalable y con mejores garantías de durabilidad, pero introduce una pieza de infraestructura nueva que no existe en el proyecto GDA y que ningún otro módulo necesita hoy. Rechazada por desproporcionada para el volumen estimado (10 GB iniciales, ver requisitos).

**B — Filesystem propio del servidor** *(seleccionada)*. Reutiliza la infraestructura ya operativa (`/gda/`, mismo servidor que aloja GitLab y el resto de volúmenes del proyecto), sin dependencias nuevas. Exige planificar manualmente el crecimiento de espacio en disco (ya señalado como requisito no funcional de escalabilidad).

**C — Servir los adjuntos directamente desde un servidor web estático (nginx/Apache), sin pasar por el microservicio.** Más eficiente para ficheros grandes, pero impide aplicar autorización por petición — contradice el requisito de que el contenido es "accesible únicamente para usuarios autenticados" y el modelo de autorización centralizada de ADR-0605. Rechazada.

## Consecuencias

### Positivas (+)

* No introduce infraestructura nueva — reutiliza el filesystem del servidor ya usado por el resto del proyecto.
* Metadatos en BBDD y binarios en disco desacoplados por ruta relativa: mover la raíz de almacenamiento no requiere migrar datos.
* Verificado por ejecución real de principio a fin (Fase 2): subida, descarga con `Content-Type`/`Content-Disposition` correctos, y borrado físico del fichero al eliminar el adjunto.

### Negativas (-)

* Escalabilidad limitada por el disco del servidor único — sin replicación ni redundancia propia de un object storage.
* La divergencia de ruta entre `local` y `dev`/`pre`/`pro` (punto 2) es una excepción nueva al patrón de perfiles idénticos que seguía el resto del backend; debe tenerse en cuenta si se automatiza el despliegue en el futuro.
* `pre` y `pro` no se han verificado todavía — se asume (política explícita del usuario: "deben seguir siendo gemelas de Desa") que tendrán la misma estructura `/gda/espacio-justicia/noticias`, pendiente de confirmar en esos servidores concretos cuando se despliegue.

### Riesgos Mitigados

* Que la ruta de almacenamiento quedara hardcodeada e incorrecta en producción sin haberse verificado nunca contra un servidor real (ya materializado una vez en desarrollo — `/data` no existía — corregido antes de llegar a `pre`/`pro`).
* Que los adjuntos quedaran accesibles sin autorización al servirse fuera del microservicio (alternativa C, descartada).

---

## Nota de actualización (2026-08-20)

El módulo propietario de esta decisión pasó de `gda-comunicacion` a `spj-comunicacion`, al segregarse Espacio Justicia en un backend independiente (ver ADR-0609, que supersede a ADR-0607). La estrategia de fondo descrita en este ADR **no cambia**: sigue siendo almacenamiento en disco local del servidor, misma ruta raíz `/gda/espacio-justicia/noticias`, mismo mecanismo de servicio autenticado vía el microservicio. Lo que cambia es solo la identidad del módulo propietario:

* Propiedad de configuración: `gda-comunicacion.storage.base-path` → `spj-comunicacion.storage.base-path`.
* Esquema de metadatos (`noticia_adjunto`): `gda_comunicacion` → `spj_comunicacion`, en la base de datos independiente `spj_01_desa`.
* Implementación: `com.ineco.gda.comunicacion.service.impl.NoticiaAdjuntoStorageServiceImpl` → `com.ineco.spj.comunicacion.service.impl.NoticiaAdjuntoStorageServiceImpl`, mismo código, mismo comportamiento.

## Referencias

* `GDA/backend/spj-comunicacion/spj-comunicacion/src/main/java/com/ineco/spj/comunicacion/service/impl/NoticiaAdjuntoStorageServiceImpl.java` — implementación real (módulo actual, ver nota de actualización).
* `GDA/backend/spj-comunicacion/spj-comunicacion/src/main/resources/config/application-{local,dev,pre,pro}.yml` — `spj-comunicacion.storage.base-path`.
* ADR-0609 (segregación de Espacio Justicia en backend independiente SPJ) — módulo propietario actual de esta decisión.
* ADR-0607 (microservicio `gda-comunicacion`, superseded por ADR-0609) — Referencias, menciona el hueco de ADR de almacenamiento nunca formalizado.
* ADR-0603 (gestión de BBDD) — los metadatos de adjunto (`noticia_adjunto`) siguen el mismo esquema propio, hoy `spj_comunicacion`.
* `.vscode/docs/Documentacion_BackEnd_EspacioJusticia_2607.md` — origen de la necesidad de este ADR (2026-07-22).
* `.vscode/docs/Documentacion_BackEnd_EspacioJusticia_2607_requisitos02.2.md` — apartado GESTOR DOCUMENTAL, convención de carpetas y corrección de ruta (2026-08-14).
* `.vscode/docs/Documentacion_BackEnd_EspacioJusticia_planaccion_2608.md` §9 — verificación real de subida/descarga/borrado de fichero (Fase 2).
