-- ==========================================
-- Esquema de monitoring_db (FASE 6, bloque B1)
-- ==========================================
-- Se ejecuta automáticamente desde /docker-entrypoint-initdb.d solo cuando el
-- volumen postgres_postgres-data está vacío. Con un volumen ya inicializado,
-- los cambios aquí no se aplican: hay que recrear el volumen o migrar.
--
-- Origen: esquema recuperado del dump monitoring_db-202601172205.backup
-- (17/01/2026). IF NOT EXISTS permite reaplicarlo sin error.
--
-- honeypot_logs: el honeypot está fuera de alcance, pero la tabla se crea
-- (vacía) porque update_attacking_no() escribe en ella.

CREATE TABLE IF NOT EXISTS public.attacking_logs (
    id                  serial PRIMARY KEY,
    "timestamp"         timestamp with time zone DEFAULT now() NOT NULL,
    log_ref             integer,
    log_type            character varying(50),
    attacking_octets    character varying(15),
    attacking_no        integer,
    attacking_ip        character varying(45),
    attacking_user      character varying(50),
    attacking_port      integer,
    attacking_country   character varying(50),
    attacking_town      character varying(50),
    attacking_long      character varying(50),
    attacking_lat       character varying(50)
);

CREATE TABLE IF NOT EXISTS public.fail2ban_logs (
    id                  serial PRIMARY KEY,
    "timestamp"         timestamp with time zone DEFAULT now() NOT NULL,
    log_ref             integer,
    log_type            character varying(50),
    attacking_octets    character varying(15),
    attacking_no        integer,
    attacking_ip        character varying(45),
    attacking_user      character varying(50),
    attacking_port      integer,
    attacking_country   character varying(50),
    attacking_town      character varying(50),
    attacking_long      character varying(50),
    attacking_lat       character varying(50)
);

CREATE TABLE IF NOT EXISTS public.kern_logs (
    id                  serial PRIMARY KEY,
    "timestamp"         timestamp with time zone DEFAULT now() NOT NULL,
    log_ref             integer,
    log_type            character varying(50),
    attacking_octets    character varying(15),
    attacking_no        integer,
    attacking_ip        character varying(45),
    attacking_user      character varying(50),
    attacking_port      integer,
    attacking_protocol  character varying(50),
    attacking_interface character varying(50),
    attacking_country   character varying(50),
    attacking_town      character varying(50),
    attacking_long      character varying(50),
    attacking_lat       character varying(50)
);

CREATE TABLE IF NOT EXISTS public.honeypot_logs (
    id                  serial PRIMARY KEY,
    "timestamp"         timestamp with time zone DEFAULT now() NOT NULL,
    log_ref             integer,
    log_type            character varying(50),
    attacking_octets    character varying(15) UNIQUE,
    attacking_no        integer,
    attacking_ip        character varying(45),
    attacking_user      character varying(50),
    attacking_port      integer,
    attacking_country   character varying(50),
    attacking_town      character varying(50),
    attacking_long      character varying(50),
    attacking_lat       character varying(50)
);
