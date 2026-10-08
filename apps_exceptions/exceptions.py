from __future__ import annotations

import errno
from collections.abc import Iterator


class ValidationException(Exception):
    def __init__(self, error_msg: str, error_no: int = errno.EFAULT) -> None:
        self.errmsg = error_msg
        self.errno = error_no

    def get_error_name(self) -> str:
        return errno.errorcode.get(self.errno) or 'EUNKNOWN'

    def __str__(self) -> str:
        return f'[{self.get_error_name()}] {self.errmsg}'


class ValidationError(ValidationException):
    def __init__(self, attribute: str, errmsg: str, errno: int = errno.EFAULT) -> None:
        self.attribute = attribute
        self.errmsg = errmsg
        self.errno = errno

    def __str__(self) -> str:
        return f'[{self.get_error_name()}] {self.attribute}: {self.errmsg}'


class ValidationErrors(ValidationException):
    def __init__(self, errors: list[ValidationError] | None = None) -> None:
        self.errors: list[ValidationError] = errors or []

    def add(self, attribute: str, errmsg: str, errno: int = errno.EINVAL) -> None:
        self.errors.append(ValidationError(attribute, errmsg, errno))

    def add_validation_error(self, validation_error: ValidationError) -> None:
        self.errors.append(validation_error)

    def add_child(self, attribute: str, child: ValidationErrors) -> None:
        for e in child.errors:
            self.add(f"{attribute}.{e.attribute}", e.errmsg, e.errno)

    def check(self) -> None:
        if self:
            raise self

    def extend(self, errors: ValidationErrors) -> None:
        for e in errors.errors:
            self.add(e.attribute, e.errmsg, e.errno)

    def __iter__(self) -> Iterator[tuple[str, str, int]]:
        for e in self.errors:
            yield e.attribute, e.errmsg, e.errno

    def __bool__(self) -> bool:
        return bool(self.errors)

    def __str__(self) -> str:
        output = ''
        for e in self.errors:
            output += str(e) + '\n'
        return output

    def __contains__(self, item: object) -> bool:
        return item in [e.attribute for e in self.errors]


class CatalogDoesNotExist(ValidationException):
    def __init__(self, path: str) -> None:
        super().__init__(f'Failed to find a catalog at {path}', errno.ENOENT)


class AppDoesNotExist(ValidationException):
    def __init__(self, path: str) -> None:
        super().__init__(f'Failed to find an app at {path}', errno.ENOENT)
