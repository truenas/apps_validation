import collections
import importlib
import os
import shutil

from jinja2 import Environment, FileSystemLoader

from .utils import RE_MODULE_VERSION


def render_templates(template_path: str, test_values: dict, lib_version: str):
    file_loader = FileSystemLoader(template_path)
    env = Environment(loader=file_loader)
    # This how filters can be introduced currently not sure how to handle it
    env.filters['make_capital'] = lambda st: st.upper()
    templates = env.get_template('docker_compose.yaml')
    libs = import_library(os.path.join(template_path, 'library'), lib_version)
    context = {
        **test_values,
        'libs': libs
    }
    return templates.render(context)


def import_library(library_path: str, lib_version: str):
    modules_context = collections.defaultdict(dict)
    for train_name in os.listdir(library_path):
        if not RE_MODULE_VERSION.findall(train_name):
            modules_context[train_name] = collections.defaultdict(dict)
            for app_name in os.listdir(os.path.join(library_path, train_name)):
                modules_context[train_name][app_name] = import_app_modules(
                    os.path.join(library_path, train_name, app_name, lib_version), lib_version)
        else:
            base_name = train_name.replace(f'_{RE_MODULE_VERSION.findall(train_name)[0]}', '')
            modules_context[base_name] = import_app_modules(
                os.path.join(library_path, train_name), train_name)

    return modules_context


def import_app_modules(modules_path: str, parent_module_name):
    def import_module_context(module_name, file_path):
        try:
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except Exception as e:
            raise Exception(f'Some changes might be introduce in this '
                            f'package {module_name.split(".")[0]} please update the package versions error: {e}')
        return module
    sub_modules_context = {}
    try:
        importlib.sys.path.append(os.path.dirname(modules_path))
        for sub_modules_file in filter(lambda p: os.path.isfile(os.path.join(modules_path, p)),
                                       os.listdir(modules_path)):
            sub_modules = sub_modules_file.removesuffix('.py')
            sub_modules_context[sub_modules] = import_module_context(
                f'{parent_module_name}.{sub_modules}', os.path.join(modules_path, sub_modules_file)
            )
    finally:
        importlib.sys.path.remove(os.path.dirname(modules_path))
        remove_pycache(modules_path)

    return sub_modules_context


def remove_pycache(library_path: str):
    for modules in filter(lambda p: os.path.exists(os.path.join(library_path, p, '__pycache__')),
                          os.listdir(library_path)):
        shutil.rmtree(os.path.join(library_path, modules, '__pycache__'))
