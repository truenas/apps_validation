import yaml

from catalog_templating.render import render_templates


def _app(tmp_path):
    (tmp_path / 'templates' / 'library').mkdir(parents=True)
    (tmp_path / 'app.yaml').write_text('name: demo\ntrain: stable\nversion: 1.0.0\nlib_version: null\n')
    (tmp_path / 'templates' / 'docker-compose.yaml').write_text(
        'services:\n'
        '  app:\n    image: "{{ values.images.image.repository }}:{{ values.images.image.tag }}"\n'
        '  db:\n    image: "{{ values.images.postgres.repository }}:{{ values.images.postgres.tag }}"\n'
    )
    return str(tmp_path)


def test_renderer_applies_overrides_to_multiple_services_and_default_is_unchanged(tmp_path):
    app = _app(tmp_path)
    values = {
        'images': {
            'image': {'repository': 'ghcr.io/example/app', 'tag': '1@sha256:' + 'a' * 64},
            'postgres': {'repository': 'postgres', 'tag': '16'},
        },
    }
    default = yaml.safe_load(render_templates(app, values)['docker-compose.yaml'])
    assert default['services']['app']['image'] == 'ghcr.io/example/app:1@sha256:' + 'a' * 64
    overridden = yaml.safe_load(render_templates(app, values | {
        'image_overrides': [
            {'image': 'image', 'registry': 'mirror.example:5000'},
            {'image': 'postgres', 'repository': 'mirror.example/database/postgres', 'tag': '16-patched'},
        ],
    })['docker-compose.yaml'])
    assert overridden['services']['app']['image'] == 'mirror.example:5000/example/app:1@sha256:' + 'a' * 64
    assert overridden['services']['db']['image'] == 'mirror.example/database/postgres:16-patched'
