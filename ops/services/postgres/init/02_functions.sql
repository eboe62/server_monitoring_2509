-- ==========================================
-- Funciones de monitoring_db (FASE 6, bloque B1)
-- ==========================================
-- Origen: función recuperada del dump monitoring_db-202601172205.backup.
--
-- update_attacking_no(): la llaman los jobs de ingesta tras cada lote.
--   - En attacking_logs, fail2ban_logs y kern_logs: attacking_no = número
--     total de registros de su attacking_octets en esa misma tabla.
--   - honeypot_logs recibe attacking_no y el log_type más grave
--     (06_login_accepted > 04 > 03 > 02 > 08) desde attacking_logs.
-- alert_risk usa attacking_no para quedarse con un registro por origen.

CREATE OR REPLACE FUNCTION public.update_attacking_no() RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Actualiza attacking_logs con su propio conteo
    WITH attack_counts AS (
        SELECT attacking_octets, COUNT(*) AS attack_count
        FROM attacking_logs
        GROUP BY attacking_octets
    )
    UPDATE attacking_logs al
    SET attacking_no = ac.attack_count
    FROM attack_counts ac
    WHERE al.attacking_octets = ac.attacking_octets
      AND al.attacking_no IS DISTINCT FROM ac.attack_count;

    -- Actualiza fail2ban_logs con su propio conteo
    WITH fb_counts AS (
        SELECT attacking_octets, COUNT(*) AS attack_count
        FROM fail2ban_logs
        GROUP BY attacking_octets
    )
    UPDATE fail2ban_logs fb
    SET attacking_no = fc.attack_count
    FROM fb_counts fc
    WHERE fb.attacking_octets = fc.attacking_octets
      AND fb.attacking_no IS DISTINCT FROM fc.attack_count;

    -- Actualiza kern_logs con su propio conteo
    WITH kern_counts AS (
        SELECT attacking_octets, COUNT(*) AS attack_count
        FROM kern_logs
        GROUP BY attacking_octets
    )
    UPDATE kern_logs kl
    SET attacking_no = kc.attack_count
    FROM kern_counts kc
    WHERE kl.attacking_octets = kc.attacking_octets
      AND kl.attacking_no IS DISTINCT FROM kc.attack_count;

    -- Transfiere attacking_no desde attacking_logs hacia honeypot_logs
    UPDATE honeypot_logs hl
    SET attacking_no = al.attacking_no
    FROM attacking_logs al
    WHERE hl.attacking_octets = al.attacking_octets
      AND hl.attacking_no IS DISTINCT FROM al.attacking_no;

    -- Transfiere log_type con prioridad según severidad
    WITH ranked_logs AS (
        SELECT
            attacking_octets,
            log_type,
            ROW_NUMBER() OVER (
                PARTITION BY attacking_octets
                ORDER BY CASE log_type
                    WHEN '06_login_accepted' THEN 5
                    WHEN '04_attempts_exceeded' THEN 4
                    WHEN '03_invalid_user' THEN 3
                    WHEN '02_no_negotiate' THEN 2
                    WHEN '08_connection_out' THEN 1
                    ELSE 0
                END DESC
            ) AS rn
        FROM attacking_logs
    )
    UPDATE honeypot_logs hl
    SET log_type = rl.log_type
    FROM ranked_logs rl
    WHERE hl.attacking_octets = rl.attacking_octets
      AND rl.rn = 1
      AND hl.log_type IS DISTINCT FROM rl.log_type;
END;
$$;
