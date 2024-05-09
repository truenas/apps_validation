import collections
import importlib
import os
import pathlib
import shutil

from jinja2 import Environment, FileSystemLoader

from apps_validation.exceptions import ValidationError
from catalog_reader.app_utils import get_app_basic_details


def render_templates(app_version_path: str, test_values: dict) -> dict:
    app_details = get_app_basic_details(app_version_path)
    if not app_details:
        raise ValidationError('app_version_path', 'Unable to retrieve app metadata from specified app version path')

    template_path = os.path.join(app_version_path, 'templates')
    if not pathlib.Path(os.path.join(template_path, 'library')).is_dir():
        return {}

    template_libs = import_library(os.path.join(template_path, 'library'), app_details)
    file_loader = FileSystemLoader(template_path)
    env = Environment(loader=file_loader)
    rendered_templates = {}
    for to_render_file in filter(
        lambda f: f.is_file() and f.name.endswith('.yaml'), pathlib.Path(template_path).iterdir()
    ):
        # TODO: Let's look to adding dynamic filter support in the future
        # env.filters['make_capital'] = lambda st: st.upper()
        rendered_templates[to_render_file.name] = env.get_template(
            to_render_file.name
        ).render(test_values | {'ix_lib': template_libs})

    return rendered_templates


def import_library(library_path: str, app_config) -> dict:
    modules_context = collections.defaultdict(dict)
    # 2 dirs which we want to import from
    global_base_lib = os.path.join(library_path, f'base_v{(app_config["lib_version"] or "").replace(".", "_")}')
    app_lib = os.path.join(
        library_path, app_config['train'], app_config['name'], f'v{app_config["version"].replace(".", "_")}'
    )
    if app_config['lib_version'] and pathlib.Path(global_base_lib).is_dir():
        modules_context['base'] = import_app_modules(global_base_lib, os.path.basename(global_base_lib))  # base_v1_0_0
    if pathlib.Path(app_lib).is_dir():
        modules_context[app_config['train']] = {
            app_config['name']: import_app_modules(app_lib, os.path.basename(app_lib))  # v1_0_1
        }

    return modules_context


def import_app_modules(modules_path: str, parent_module_name) -> dict:
    def import_module_context(module_name, file_path):
        try:
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except Exception as e:
            raise Exception(
                f'Unable to import module {module_name!r} from {file_path!r}: {e!r}.\n\n'
                'This could be due to various reasons with primary being:\n1) The module is not a valid python module '
                'which can be imported i.e might have syntax errors\n2) The module has already been imported and '
                'then has been changed but the version for the module has not been bumped.'
            )
        return module

    sub_modules_context = {}
    try:
        importlib.sys.path.append(os.path.dirname(modules_path))
        for sub_modules_file in filter(
            lambda p: os.path.isfile(os.path.join(modules_path, p)) and p.endswith('.py'), os.listdir(modules_path)
        ):
            sub_modules = sub_modules_file.removesuffix('.py')
            sub_modules_context[sub_modules] = import_module_context(
                f'{parent_module_name}.{sub_modules}', os.path.join(modules_path, sub_modules_file)
            )
    finally:
        importlib.sys.path.remove(os.path.dirname(modules_path))
        remove_pycache(modules_path)

    return sub_modules_context


def remove_pycache(library_path: str):
    shutil.rmtree(os.path.join(library_path, '__pycache__'), ignore_errors=True)
