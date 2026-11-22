-- ==========================================
-- Migración B10-1: 08_connection_out -> 05_connection_close
-- ==========================================
-- Esas filas son desconexiones antes de autenticarse ("Connection closed/reset",
-- "Disconnected"), no conexiones salientes. El número ordena por gravedad:
-- hasta 05 nadie ha entrado; desde 06, sí.
--
-- Se aplica con: make db-migrate-log-types (después de make deploy).
-- Es idempotente: si se repite, no cambia nada.
-- Una sola transacción: o se aplica entera o nada.
-- Toma el mismo turno que update_attacking_no() para no cruzarse con la ingesta.
-- Vuelta atrás: el mismo UPDATE con los nombres al revés (y revertir el código).

BEGIN;

DO $$ BEGIN PERFORM pg_advisory_xact_lock(hashtext('monitoring.attacking_logs')); END $$;

WITH a AS (
    UPDATE attacking_logs SET log_type = '05_connection_close'
    WHERE log_type = '08_connection_out'
    RETURNING 1
)
SELECT 'attacking_logs' AS tabla, COUNT(*) AS filas_renombradas FROM a;

WITH h AS (
    UPDATE honeypot_logs SET log_type = '05_connection_close'
    WHERE log_type = '08_connection_out'
    RETURNING 1
)
SELECT 'honeypot_logs' AS tabla, COUNT(*) AS filas_renombradas FROM h;

COMMIT;
