from typing import Any, Iterable

from django import template

register = template.Library()


@register.filter
def index(sequence: list[Any], position: int) -> Any | None:
    try:
        return sequence[int(position)]
    except (IndexError, TypeError, ValueError):
        return None


@register.filter
def multiply(value: Any, arg: Any) -> None | int:
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return None


@register.filter
def add(value: Any, arg: Any) -> None | int:
    try:
        return int(value) + int(arg)
    except (ValueError, TypeError):
        return None


@register.filter
def range_filter(value: int) -> Iterable[int]:
    """
    주어진 값까지의 범위를 생성합니다 (0부터 value-1까지).
    """
    return range(value)
