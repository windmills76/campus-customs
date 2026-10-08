import re

# Defense-in-depth backstop for the "never store payment/ID numbers" rule in
# prompts/prompt.md: strip anything that looks like a card number or SSN
# before it ever reaches the model or the database. This doesn't depend on
# the model choosing to comply — it runs in code on every chat message.
_SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
_CARD_LIKE_RE = re.compile(r"\b(?:\d[ -]?){13,19}\b")
_REDACTED = "[redacted]"


def redact_sensitive(text: str) -> str:
    text = _SSN_RE.sub(_REDACTED, text)
    text = _CARD_LIKE_RE.sub(_REDACTED, text)
    return text
