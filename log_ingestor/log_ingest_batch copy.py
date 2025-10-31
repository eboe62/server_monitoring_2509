# Reemplaza parse_timestamp() por esto
def parse_timestamp(log_line):
    try:
        # ISO 8601
        match_iso = re.match(r"^([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]+[+-][0-9]{2}:[0-9]{2})", log_line)
        if match_iso:
            return datetime.fromisoformat(match_iso.group(1))

        # Formato syslog clásico
        match_sys = re.match(r"^([A-Z][a-z]{2}\s+[0-9]{1,2}\s[0-9:]{8})", log_line)
        if match_sys:
            return datetime.strptime(match_sys.group(1), "%b %d %H:%M:%S")
    except Exception:
        pass
    return None
