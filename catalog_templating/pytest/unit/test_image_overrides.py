import copy

import pytest

from apps_exceptions import ValidationError
from catalog_templating.image_overrides import apply_image_overrides


IMAGES = {
    'image': {'repository': 'ghcr.io/example/app', 'tag': '1.2.3@sha256:' + 'a' * 64},
    'postgres_image': {'repository': 'postgres', 'tag': '16'},
    'redis_image': {'repository': 'redis', 'tag': '7@sha256:' + 'b' * 64},
}


def test_empty_and_missing_overrides_preserve_legacy_values():
    values = {'images': copy.deepcopy(IMAGES)}
    assert apply_image_overrides(values) == values
    assert apply_image_overrides({'images': copy.deepcopy(IMAGES)})['images'] == IMAGES


def test_registry_override_preserves_namespace_tag_and_digest():
    result = apply_image_overrides({
        'images': copy.deepcopy(IMAGES),
        'image_overrides': [{'image': 'image', 'registry': 'registry.example:5000'}],
    })
    assert result['images']['image'] == {
        'repository': 'registry.example:5000/example/app',
        'tag': '1.2.3@sha256:' + 'a' * 64,
    }


def test_changed_tag_drops_old_immutable_pin_unless_new_digest_is_given():
    result = apply_image_overrides({
        'images': copy.deepcopy(IMAGES),
        'image_overrides': [{'image': 'image', 'tag': 'patched'}],
    })
    assert result['images']['image']['tag'] == 'patched'


def test_oci_repository_names_allow_repeated_separators_and_registry_ports():
    values = {'images': {'image': {'repository': 'ghcr.io/example/foo__bar-2', 'tag': '1'}}}
    result = apply_image_overrides({
        **values,
        'image_overrides': [{'image': 'image', 'registry': 'mirror.example:5000'}],
    })
    assert result['images']['image']['repository'] == 'mirror.example:5000/example/foo__bar-2'


def test_localhost_is_a_valid_explicit_registry():
    result = apply_image_overrides({
        'images': copy.deepcopy(IMAGES),
        'image_overrides': [{'image': 'image', 'registry': 'localhost'}],
    })
    assert result['images']['image']['repository'] == 'localhost/example/app'


def test_multi_image_full_replacement_only_targets_selected_dependencies():
    result = apply_image_overrides({
        'images': copy.deepcopy(IMAGES),
        'image_overrides': [
            {'image': 'image', 'repository': 'registry.example/app', 'tag': 'patched', 'digest': 'sha256:' + 'c' * 64},
            {'image': 'postgres_image', 'registry': 'mirror.example', 'tag': '16-alpine'},
        ],
    })
    assert result['images']['image']['tag'] == 'patched@sha256:' + 'c' * 64
    assert result['images']['postgres_image'] == {'repository': 'mirror.example/library/postgres', 'tag': '16-alpine'}
    assert result['images']['redis_image'] == IMAGES['redis_image']


@pytest.mark.parametrize('override', [
    {'image': 'missing', 'tag': 'latest'},
    {'image': 'image', 'registry': 'bad registry'},
    {'image': 'image', 'repository': 'https://registry.example/app'},
    {'image': 'image', 'digest': 'sha256:bad'},
    {'image': 'image', 'registry': 'mirror.example:65536'},
    {'image': 'image', 'registry': 'mirror'},
    {'image': 'image', 'repository': 'mirror.example:65536/app'},
    {'image': 'image', 'registry': 'mirror.example', 'repository': 'mirror/app'},
    {'image': 'image', 'unexpected': 'value'},
    {'image': 'image', 'tag': 123},
])
def test_invalid_overrides_are_rejected(override):
    with pytest.raises(ValidationError):
        apply_image_overrides({'images': copy.deepcopy(IMAGES), 'image_overrides': [override]})


@pytest.mark.parametrize('image', [None, 'invalid', {'repository': 12, 'tag': 'latest'}])
def test_selected_malformed_image_definitions_raise_validation_error(image):
    with pytest.raises(ValidationError):
        apply_image_overrides({'images': {'image': image}, 'image_overrides': [{'image': 'image'}]})
