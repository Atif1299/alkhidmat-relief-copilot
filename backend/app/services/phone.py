"""Pakistani mobile numbers: find, normalise to 03XXXXXXXXX, and require one on intake."""

from __future__ import annotations

import re
from typing import Optional

# 03XXXXXXXXX, 3XXXXXXXXX after +92 / 0092 / 92. Separators are stripped first.
_MOBILE = re.compile(r"(?:\+92|0092|92|0)(3\d{9})(?!\d)")

PHONE_REQUIRED = (
    "Add a mobile number (yours or a family member's) so the desk can reach you "
    "and you can check your request later."
)
PHONE_INVALID = "Enter a Pakistani mobile number like 0300 1234567."


def find_mobile(text: Optional[str]) -> Optional[str]:
    """Return the first mobile number in `text` as 03XXXXXXXXX, or None."""
    if not text:
        return None
    compact = re.sub(r"[\s\-().]", "", text)
    match = _MOBILE.search(compact)
    return f"0{match.group(1)}" if match else None


def message_with_phone(message: str, phone_field: Optional[str]) -> tuple[str, str]:
    """Resolve the requester's mobile; return (message, phone).

    Raises ValueError with a citizen-facing reason when no valid number is given.
    The phone field wins over any number in the text. The number is appended in
    03XXXXXXXXX form when the message does not already contain it, so staff see
    it in the request text.
    """
    if phone_field and phone_field.strip():
        phone = find_mobile(phone_field)
        if phone is None:
            raise ValueError(PHONE_INVALID)
    else:
        phone = find_mobile(message)
        if phone is None:
            raise ValueError(PHONE_REQUIRED)
    if phone not in re.sub(r"[\s\-().]", "", message):
        message = f"{message.rstrip()} Phone {phone}"
    return message, phone
