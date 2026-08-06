from config.sentry import FILTERED, before_send


def _event_with_pii():
    """A synthetic Sentry event with personal data in the request body and a valid trace."""
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

    # The request body and the cookies are stripped whole — they hold personal data.
    assert event["request"]["data"] == FILTERED
    assert event["request"]["cookies"] == FILTERED
    # No personal-data value may appear anywhere in the event.
    blob = str(event)
    assert "Иван" not in blob
    assert "+74950000000" not in blob
    assert "ivan@example.com" not in blob
    assert "хочу 20 канистр" not in blob


def test_before_send_keeps_diagnostics():
    event = before_send(_event_with_pii(), hint={})

    # URL, method, exception type/value and the stack trace are preserved.
    assert event["request"]["url"] == "https://example.com/zayavka/"
    assert event["request"]["method"] == "POST"
    exc = event["exception"]["values"][0]
    assert exc["type"] == "ValueError"
    assert exc["stacktrace"]["frames"][0]["filename"] == "apps/leads/views.py"
    # Non-personal fields in extra stay.
    assert event["extra"]["order_id"] == 7
    # The personal-data field comment in extra is wiped.
    assert event["extra"]["comment"] == FILTERED


def _event_with_stacktrace_vars():
    """An event with personal data in stack frame locals (as in a real traceback)."""
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
    # payload is a name from PII_VAR_NAMES → stripped whole.
    assert frame_vars["payload"] == FILTERED
    # The non-personal variable stays (the diagnostics are not lost).
    assert frame_vars["price"] == "1000"
    # No personal-data value appears anywhere in the event.
    blob = str(event)
    assert "Иван Тестов" not in blob
    assert "+74950000000" not in blob
    # The exception type and message are preserved.
    assert event["exception"]["values"][0]["type"] == "RuntimeError"
