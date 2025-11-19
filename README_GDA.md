# 🧩 Proyecto GDA Tests — E2E Automation (v251009)

![Python](https://img.shields.io/badge/Python-3.10-blue.svg)
![Docker](https://img.shields.io/badge/Docker-enabled-0db7ed.svg)
![Status](https://img.shields.io/badge/Status-Operational-success.svg)
![License](https://img.shields.io/badge/Environment-INECO_GdAct_DESA-orange.svg)

---

## 📖 Descripción general

**GDA Tests** automatiza la ejecución diaria de **tests end-to-end (E2E)** sobre las llamadas del **API Gateway** de la aplicación GDA.  
El sistema está desplegado en un **servidor RedHat** con **microservicios Java + Vue** y se integra con el **relay SMTP local** para enviar informes automáticos por correo.

Los tests se ejecutan de forma programada mediante un **cron diario a las 05:00 a.m.**.  
Cada ejecución genera un informe detallado y autocontenido con resultados de éxito o fallo por endpoint.

---

## 🏗️ Infraestructura en servidor

Servidor actual:  
`ineco.ietreir01sdes`

Ruta de instalación:  
`/home/ineco/gda-tests`


---

## 📂 Estructura del proyecto

```
/gda-tests
│
├── config.py                       # Configuración SMTP, BBDD y utilidades
├── utils_app.py                    # Login OAuth y helpers de autenticación
├── report.py                       # Generación de informes de resultados
├── test_runner_methods.py          # Motor principal de ejecución de tests
├── runner_methods.yaml             # Colección de endpoints y definiciones DELETE
├── runner_methods_completo.yaml    # Copia maestra con todas las rutas
├── requirements.txt                # Dependencias Python
├── Dockerfile                      # Imagen base para entorno aislado
├── .env                            # Variables de entorno de ejecución
└── utils_app.py                    # Funciones auxiliares de aplicación
```

## ⚙️ Configuración técnica

⏱️ **Cron / Logs**

```bash
# Cron configurado:
        Construcción y ejecución diaria de los tests
        0 5 * * * docker build -t gda-tests /home/ineco/gda-tests
        5 5 * * * docker run --rm --network=host -v /home/ineco/gda-tests:/app gda-tests python3 test_runner_methods.py >> /var/log/gda-tests.log 2>&1

# El log de cada ejecución se almacena en:
        /var/log/gda-tests.log
```

🐳 **Dockerfile**
```dockerfile
FROM python:3.10-slim

WORKDIR /app
# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código y config
COPY . .
# Ejecución por defecto

CMD ["pytest", "-v"]
```

📦 **Dependencias (requirements.txt)**

```
psycopg2-binary
python-dotenv
requests
pytest
PyYAML>=6.0
```

⚙️ **Variables de entorno (.env)**

```env
SMTP_RELAY_CONTAINER_NAME=smtp-relay

# Configuración SMTP común
SMTP_SERVER = smtp.postmarkapp.com
SMTP_PORT = 9999

# Postmark SMTP credentials
EMAIL_FROM = noreply@tudominio.com
EMAIL_DOMAIN = tudominio.com
EMAIL_TO = contacto@tudominio.com

# Redes permitidas para relay
MYNETWORKS = 127.0.0.0/8 172.16.0.0/12 [::1]/128

# Configuración de la base de datos
# DB_HOST = "localhost"  # Si estás ejecutando en el mismo contenedor o servidor
DB_HOST = postgres
DB_NAME = monitoring_db
DB_USER = user
DB_PASSWORD = 999999999
DB_PORT = 9999
```

---

## 🧠 Componentes principales

### 🧩 `config.py`
Carga `.env` con `python-dotenv`.  
Configura SMTP, PostgreSQL y logging.  
Expone funciones clave:         
`connect_db()`,         
`close_db()`,   
`send_email()`,         
`to_snake_case()`,      
`log_info()`.

### 🔐 `utils_app.py`
Gestiona login contra `BASE_URL/oauth/login`.  
Retorna un token JWT válido.
Incluye auth_headers(token) para autorizar peticiones

### 🧾 `report.py`
Genera informes en texto plano  
Registra cada test (OK / ERROR / tiempo / URL)  
Registra tiempo, URL y estado de cada test.  
Resumen final `n fallidos / n totales`.  
No se envía correo si todos los tests pasan.

Produce un resumen final:

        📊 Informe de ejecución de tests
        ========================================
        ✅ POST /super/iniciativas: 200 [1.21s]
        ✅ DELETE gda_estructura.iniciativa WHERE id = 9876 → 1 filas
        ----------------------------------------
        ❌ POST /super/personas: esperado 200, obtenido 500 [0.97s]
        URL: https://gda-desa.ineco.es/api/super/personas
        ========================================
        📊 Resumen: 1 fallidos / 2 totales
        ========================================

### 🧪 `test_runner_methods.py`
Motor que ejecuta dinámicamente los tests definidos en `runner_methods.yaml`.   
Soporta métodos GET, POST, y PUT        
Valida códigos de estado, expande respuestas JSON.      
Detecta respuestas **no JSON**.   
Endpoints con JWT o binarios (Excel) no generan error      
Respuestas vacías o texto plano se omiten silenciosamente.
DELETE dinámico con claves `camelCase` y anidados (`detalle.id → detalle_id`).  
Envía correo solo si existen tests fallidos.    

### 🧪 `runner_methods.yaml`
Define cada endpoint, método, payload y operaciones DELETE.

        Ejemplo YAML:
        - url: "/super/iniciativas"
        method: "POST"
        body:
            nombre: "Test iniciativa auto"
            tipoIniciativaId: 1
        delete:
            - table: "gda_estructura.iniciativa"
            key_field: "id"

---

## 🔁 Flujo de ejecución
1. Cron construye la imagen Docker.
2. El contenedor ejecuta test_runner_methods.py.
3. Se realiza login y se obtiene token JWT.
3. Se procesan los endpoints definidos en runner_methods.yaml.
4. Se validan respuestas y se limpian registros asociados al test.
5. Se genera y envía un informe por correo solo si hay fallos.
6. Se registran los resultados en `/var/log/gda-tests.log`.

---

## 💡 Recomendaciones

- Mantener `ALLOW_PHYSICAL_DELETE=False` en productivo.  
- Añadir nuevos endpoints en `runner_methods.yaml`.  
- Revisar `/var/log/gda-tests.log` tras cada ejecución.

---

## 🧾 Licencia y autoría
Proyecto interno **INECO - GdAct DESA**  
Desarrollado por: **enrique.orellana@ineco.com**  
📅 **Última actualización:** 2025-10-10
