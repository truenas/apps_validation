"""Apply user supplied image overrides before an app template is rendered.

The catalog stores images as ``repository`` and ``tag`` pairs.  Keeping the
override here means every catalog app gets the same behavior, including apps
with helper, database, or cache images, without changing each app template.
"""

import re

from apps_exceptions import ValidationError


_REGISTRY = re.compile(r'^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)(?:\.(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?))*(?::[0-9]{1,5})?$')
_REPOSITORY = re.compile(r'^[a-z0-9]+(?:[._-]+[a-z0-9]+)*(?::[0-9]{1,5})?(?:/[a-z0-9]+(?:[._-]+[a-z0-9]+)*)*$')
_TAG = re.compile(r'^[A-Za-z0-9_][A-Za-z0-9_.-]{0,127}$')
_DIGEST = re.compile(r'^sha256:[0-9a-f]{64}$')


def _split_tag(value: str) -> tuple[str, str]:
    tag, separator, digest = value.partition('@')
    return tag, digest if separator else ''


def _has_registry(repository: str) -> bool:
    first = repository.split('/', 1)[0]
    return first == 'localhost' or '.' in first or ':' in first


def _repository_path(repository: str) -> str:
    """Return the path below a registry, including Docker Hub's library namespace."""
    if _has_registry(repository) and '/' in repository:
        return repository.split('/', 1)[1]
    return repository if '/' in repository else f'library/{repository}'


def _validate(value: str, pattern: re.Pattern, field: str) -> None:
    if not value or not pattern.fullmatch(value):
        raise ValidationError(field, f'Invalid image {field}: {value!r}')


def _validate_registry(value: str, field: str) -> None:
    _validate(value, _REGISTRY, field)
    if not _has_registry(value):
        raise ValidationError(field, 'Registry must be a fully qualified host, localhost, or include an explicit port')
    port = value.rpartition(':')[2] if ':' in value else ''
    if port and not 1 <= int(port) <= 65535:
        raise ValidationError(field, f'Invalid image registry port: {port!r}')


def _validate_repository(value: str, field: str) -> None:
    _validate(value, _REPOSITORY, field)
    first = value.split('/', 1)[0]
    if ':' in first:
        port = first.rpartition(':')[2]
        if not 1 <= int(port) <= 65535:
            raise ValidationError(field, f'Invalid image registry port: {port!r}')


def apply_image_overrides(values: dict) -> dict:
    """Return a copy of *values* with validated ``image_overrides`` applied.

    An override is a dict with ``image`` (an image key) and any of
    ``registry``, ``repository``, ``tag`` and ``digest``. Empty values are
    ignored. The original image tag and digest are retained for fields that
    are omitted, which makes registry-only overrides safe for pinned images.
    """
    overrides = values.get('image_overrides') or []
    if not isinstance(overrides, list):
        raise ValidationError('image_overrides', 'Image overrides must be a list')
    if 'images' not in values:
        if overrides:
            raise ValidationError('images', 'Image overrides require an images map')
        return dict(values)
    images = values['images']
    if not isinstance(images, dict):
        raise ValidationError('images', 'Images must be a dictionary')
    result = {**values, 'images': dict(images)}
    seen = set()
    for index, override in enumerate(overrides):
        field = f'image_overrides.{index}'
        if not isinstance(override, dict):
            raise ValidationError(field, 'Image override must be a dictionary')
        unknown = set(override) - {'image', 'registry', 'repository', 'tag', 'digest'}
        if unknown:
            raise ValidationError(field, f'Unknown image override fields: {sorted(unknown)!r}')
        key = override.get('image', '')
        if not isinstance(key, str) or key not in result['images']:
            raise ValidationError(f'{field}.image', f'Unknown image key: {key!r}')
        if key in seen:
            raise ValidationError(f'{field}.image', f'Duplicate image override: {key!r}')
        seen.add(key)
        image = result['images'][key]
        if not isinstance(image, dict):
            raise ValidationError(f'images.{key}', 'Image definition must be a dictionary')
        image = result['images'][key] = dict(image)
        repository = image.get('repository', '')
        original_tag = image.get('tag', '')
        if not isinstance(repository, str) or not isinstance(original_tag, str):
            raise ValidationError(f'images.{key}', 'Image repository and tag must be strings')
        tag, digest = _split_tag(original_tag)
        _validate_repository(repository, f'{field}.repository')
        _validate(tag, _TAG, f'{field}.tag')
        if digest:
            _validate(digest, _DIGEST, f'{field}.digest')
        requested_repository = override.get('repository') or ''
        registry = override.get('registry') or ''
        requested_tag = override.get('tag') or ''
        requested_digest = override.get('digest') or ''
        if any(value is not None and not isinstance(value, str) for value in (
            override.get('registry'), override.get('repository'), override.get('tag'), override.get('digest')
        )):
            raise ValidationError(field, 'Image override values must be strings')
        if requested_repository and registry:
            raise ValidationError(field, 'Specify repository or registry, not both')
        if requested_repository:
            _validate_repository(requested_repository, f'{field}.repository')
            repository = requested_repository
        elif registry:
            _validate_registry(registry, f'{field}.registry')
            repository = f'{registry}/{_repository_path(repository)}'
        changed_reference = bool(requested_repository or requested_tag)
        if requested_tag:
            _validate(requested_tag, _TAG, f'{field}.tag')
            tag = requested_tag
        if requested_digest:
            _validate(requested_digest, _DIGEST, f'{field}.digest')
            digest = requested_digest
        image['repository'] = repository
        # A changed tag/repository cannot safely retain the old immutable pin.
        # Registry-only rewrites retain it; callers changing the reference must
        # provide a new digest when they want pinning.
        if changed_reference and not requested_digest:
            digest = ''
        image['tag'] = f'{tag}@{digest}' if digest else tag
    return result
