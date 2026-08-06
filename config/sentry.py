"""Personal-data scrubber for Sentry events (152-FZ: names/phones/emails never leave the country)."""

# Keys whose values count as personal data and are stripped from events.
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
# Names of stack frame locals that may carry personal data as a whole
# (a Lead object, a form body, a payload) — the value is wiped entirely.
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
    """Wipe the values of PII keys in a mapping (recursively through nested dicts)."""
    if not isinstance(data, dict):
        return data
    for key, value in data.items():
        if key.lower() in PII_KEYS:
            data[key] = FILTERED
        elif isinstance(value, dict):
            _scrub_mapping(value)
    return data


def _scrub_frames(exception):
    """Wipe personal data from stack frame locals (chained exceptions included)."""
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
                    # A whole object variable (Lead, payload, form) — cut at the root.
                    frame_vars[var_name] = FILTERED
                elif isinstance(frame_vars[var_name], dict):
                    # A nested dict — cleaned by PII keys (name/phone/email/...).
                    _scrub_mapping(frame_vars[var_name])
    return


def before_send(event, hint):
    """Called by Sentry before sending. Strips personal data, keeps the diagnostics."""
    request = event.get("request")
    if isinstance(request, dict):
        # The request body (the lead form POST) and the cookies as a whole — personal data.
        if "data" in request:
            request["data"] = FILTERED
        if "cookies" in request:
            request["cookies"] = FILTERED

    # In case personal data ended up in extra/contexts.
    if isinstance(event.get("extra"), dict):
        _scrub_mapping(event["extra"])
    if isinstance(event.get("contexts"), dict):
        _scrub_mapping(event["contexts"])

    # Stack frame locals (that is where the Lead object / form body / payload live).
    _scrub_frames(event.get("exception"))
    _scrub_frames(event.get("threads"))

    return event
