from config.sentry import FILTERED, before_send


def _event_with_pii():
    """Синтетическое событие Sentry с ПДн в теле запроса и валидным трейсом."""
    return {
        "request": {
            "url": "https://example.com/zayavka/",
            "method": "POST",
            "data": {
                "name": "Иван",
                "phone": "+74950000000",
                "email": "ivan@example.com",
            },
            "cookies": {"sessionid": "secret"},
        },
        "exception": {
            "values": [
                {
                    "type": "ValueError",
                    "value": "boom",
                    "stacktrace": {
                        "frames": [{"filename": "apps/leads/views.py", "lineno": 42}]
                    },
                }
            ],
        },
        "extra": {"comment": "хочу 20 канистр", "order_id": 7},
    }


def test_before_send_strips_request_pii():
    event = before_send(_event_with_pii(), hint={})

    # Тело запроса и куки вырезаны целиком — там ПДн.
    assert event["request"]["data"] == FILTERED
    assert event["request"]["cookies"] == FILTERED
    # Значения ПДн не должны встречаться нигде в событии.
    blob = str(event)
    assert "Иван" not in blob
    assert "+74950000000" not in blob
    assert "ivan@example.com" not in blob
    assert "хочу 20 канистр" not in blob


def test_before_send_keeps_diagnostics():
    event = before_send(_event_with_pii(), hint={})

    # URL, метод, тип/значение исключения, стектрейс — сохранены.
    assert event["request"]["url"] == "https://example.com/zayavka/"
    assert event["request"]["method"] == "POST"
    exc = event["exception"]["values"][0]
    assert exc["type"] == "ValueError"
    assert exc["stacktrace"]["frames"][0]["filename"] == "apps/leads/views.py"
    # Не-ПДн поля в extra остаются.
    assert event["extra"]["order_id"] == 7
    # ПДн-поле comment в extra затёрто.
    assert event["extra"]["comment"] == FILTERED


def _event_with_stacktrace_vars():
    """Событие с ПДн в локальных переменных кадра стектрейса (как реальный traceback)."""
    return {
        "exception": {
            "values": [
                {
                    "type": "RuntimeError",
                    "value": "Не удалось рассчитать цену заявки",
                    "stacktrace": {
                        "frames": [
                            {
                                "filename": "<console>",
                                "function": "level_1",
                                "vars": {
                                    "payload": {
                                        "name": "Иван Тестов",
                                        "phone": "+74950000000",
                                    },
                                    "price": "1000",
                                },
                            }
                        ],
                    },
                }
            ],
        },
    }


def test_before_send_strips_stacktrace_vars():
    event = before_send(_event_with_stacktrace_vars(), hint={})

    frame_vars = event["exception"]["values"][0]["stacktrace"]["frames"][0]["vars"]
    # payload — имя из PII_VAR_NAMES → вырезан целиком.
    assert frame_vars["payload"] == FILTERED
    # Не-ПДн переменная осталась (диагностика не потеряна).
    assert frame_vars["price"] == "1000"
    # Значений ПДн нет нигде в событии.
    blob = str(event)
    assert "Иван Тестов" not in blob
    assert "+74950000000" not in blob
    # Тип/сообщение исключения сохранены.
    assert event["exception"]["values"][0]["type"] == "RuntimeError"
