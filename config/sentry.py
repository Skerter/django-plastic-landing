"""Скруббер ПДн для событий Sentry (152-ФЗ: имена/телефоны/email не уходят за рубеж)."""

# Ключи, значения которых считаем персональными данными и вырезаем из событий.
PII_KEYS = frozenset(
    {
        "name",
        "phone",
        "email",
        "comment",
        "first_name",
        "last_name",
        "username",
    }
)
# Имена локальных переменных в кадрах стектрейса, которые целиком могут нести ПДн
# (объект Lead, тело формы, payload и т.п.) — затираем значение целиком.
PII_VAR_NAMES = frozenset(
    {
        "payload",
        "lead",
        "form",
        "cleaned_data",
        "data",
        "request",
        "post",
        "instance",
    }
)

FILTERED = "[Filtered]"


def _scrub_mapping(data):
    """Затереть значения PII-ключей в словаре (рекурсивно по вложенным dict)."""
    if not isinstance(data, dict):
        return data
    for key, value in data.items():
        if key.lower() in PII_KEYS:
            data[key] = FILTERED
        elif isinstance(value, dict):
            _scrub_mapping(value)
    return data


def _scrub_frames(exception):
    """Затереть ПДн в локальных переменных кадров стектрейса (chained-исключения тоже)."""
    if not isinstance(exception, dict):
        return
    for value in exception.get("values", []):
        stacktrace = value.get("stacktrace")
        if not isinstance(stacktrace, dict):
            continue
        for frame in stacktrace.get("frames", []):
            frame_vars = frame.get("vars")
            if not isinstance(frame_vars, dict):
                continue
            for var_name in frame_vars:
                if var_name.lower() in PII_VAR_NAMES:
                    # Переменная-объект целиком (Lead, payload, form) — режем под корень.
                    frame_vars[var_name] = FILTERED
                elif isinstance(frame_vars[var_name], dict):
                    # Вложенный dict — чистим по PII-ключам (name/phone/email/...).
                    _scrub_mapping(frame_vars[var_name])
    return


def before_send(event, hint):
    """Вызывается Sentry перед отправкой. Вырезает ПДн, сохраняя диагностику."""
    request = event.get("request")
    if isinstance(request, dict):
        # Тело запроса (POST лидформы) и куки целиком — там ПДн.
        if "data" in request:
            request["data"] = FILTERED
        if "cookies" in request:
            request["cookies"] = FILTERED

    # На случай, если ПДн попали в extra/contexts.
    if isinstance(event.get("extra"), dict):
        _scrub_mapping(event["extra"])
    if isinstance(event.get("contexts"), dict):
        _scrub_mapping(event["contexts"])

    # Локальные переменные в кадрах стектрейса (там объект Lead / тело формы / payload).
    _scrub_frames(event.get("exception"))
    _scrub_frames(event.get("threads"))

    return event
