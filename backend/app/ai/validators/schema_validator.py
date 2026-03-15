"""Validate AI outputs against Pydantic schemas and business rules."""

import logging

from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)


def validate_output(data: dict, schema: type[BaseModel]) -> tuple[BaseModel | None, list[str]]:
    """Validate AI output against a Pydantic schema.

    Returns: (validated_model, errors)
    """
    try:
        validated = schema.model_validate(data)
        return validated, []
    except ValidationError as e:
        errors = [f"{err['loc']}: {err['msg']}" for err in e.errors()]
        logger.warning(f"AI output validation failed: {errors}")
        return None, errors


def sanitize_text(text: str, max_length: int = 200) -> str:
    """Sanitize text output from AI."""
    # Strip HTML tags
    import re
    text = re.sub(r"<[^>]+>", "", text)
    # Truncate
    if len(text) > max_length:
        text = text[:max_length].rstrip() + "..."
    return text.strip()
