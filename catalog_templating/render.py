import collections
import contextlib
import importlib
import os
import shutil

from jinja2 import Environment, FileSystemLoader

from apps_exceptions import ValidationError
from catalog_reader.app_utils import get_app_basic_details
from catalog_reader.names import get_app_library_dir_name_from_version, get_base_library_dir_name_from_version


def render_templates(app_version_path: str, test_values: dict) -> dict:
    app_details = get_app_basic_details(app_version_path)
    if not app_details:
        raise ValidationError('app_version_path', 'Unable to retrieve app metadata from specified app version path')

    template_path = os.path.join(app_version_path, 'templates')
    if not os.path.isdir(os.path.join(template_path, 'library')):
        return {}

    template_libs = import_library(os.path.join(template_path, 'library'), app_details)
    file_loader = FileSystemLoader(template_path)
    env = Environment(loader=file_loader, extensions=["jinja2.ext.do", "jinja2.ext.loopcontrols", "jinja2.ext.debug"])
    rendered_templates = {}
    with os.scandir(template_path) as sdir:
        for i in filter(lambda x: x.is_file() and x.name.endswith('.yaml'), sdir):
            # TODO: Let's look to adding dynamic filter support in the future
            # env.filters['make_capital'] = lambda st: st.upper()
            rendered_templates[i.name] = env.get_template(i.name).render(
                {'ix_lib': template_libs, 'values': test_values}
            )

    return rendered_templates


def import_library(library_path: str, app_config) -> dict:
    modules_context = collections.defaultdict(dict)
    # 2 dirs which we want to import from
    global_base_lib = os.path.join(library_path, get_base_library_dir_name_from_version(app_config['lib_version']))
    app_lib = os.path.join(
        library_path, app_config['train'], app_config['name'],
        get_app_library_dir_name_from_version(app_config['version'])
    )
    additional_package_syspath = []
    if app_config['lib_version'] and os.path.isdir(global_base_lib):
        modules_context['base'] = import_app_modules(global_base_lib, os.path.basename(global_base_lib))  # base_v1_0_0
        additional_package_syspath.append(global_base_lib)
    if os.path.isdir(app_lib):
        modules_context[app_config['train']] = {
            app_config['name']: import_app_modules(
                app_lib, os.path.basename(app_lib), additional_package_syspath
            )  # v1_0_1
        }

    return modules_context


def import_app_modules(
    modules_path: str,
    parent_module_name: str,
    additional_package_syspath: list | None = None
) -> dict:

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

    additional_package_syspath = (additional_package_syspath or []) + [modules_path]
    sub_modules_context = {}
    try:
        importlib.sys.path.extend([os.path.dirname(entry) for entry in additional_package_syspath])
        with os.scandir(modules_path) as sdir:
            for i in filter(lambda x: x.is_file() and x.name.endswith('.py'), sdir):
                sub_modules = i.name.removesuffix('.py')
                sub_modules_context[sub_modules] = import_module_context(
                    f'{parent_module_name}.{sub_modules}', os.path.join(modules_path, i.name)
                )
    finally:
        for entry in additional_package_syspath:
            with contextlib.suppress(ValueError):
                importlib.sys.path.remove(entry)

            remove_pycache(entry)

    return sub_modules_context


def remove_pycache(library_path: str):
    shutil.rmtree(os.path.join(library_path, '__pycache__'), ignore_errors=True)
