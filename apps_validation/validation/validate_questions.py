import typing
import yaml

from apps_schema.variable import Variable
from apps_validation.exceptions import ValidationErrors
from catalog_reader.questions import CUSTOM_PORTALS_ENABLE_KEY, CUSTOM_PORTAL_GROUP_KEY
from catalog_reader.questions_util import CUSTOM_PORTALS_KEY

from .utils import validate_key_value_types


def validate_questions_yaml(questions_yaml_path: str, schema: str):
    verrors = ValidationErrors()

    with open(questions_yaml_path, 'r') as f:
        try:
            questions_config = yaml.safe_load(f.read())
        except yaml.YAMLError:
            verrors.add(schema, 'Must be a valid yaml file')
        else:
            if not isinstance(questions_config, dict):
                verrors.add(schema, 'Must be a dictionary')

    verrors.check()

    validate_key_value_types(
        questions_config, (
            ('groups', list), ('questions', list), ('portals', dict, False), (CUSTOM_PORTALS_ENABLE_KEY, bool, False),
            (CUSTOM_PORTAL_GROUP_KEY, str, False),
        ), verrors, schema
    )

    verrors.check()

    groups = []
    for index, group in enumerate(questions_config['groups']):
        if not isinstance(group, dict):
            verrors.add(f'{schema}.groups.{index}', 'Type of group should be a dictionary.')
            continue

        if group.get('name'):
            groups.append(group['name'])

        validate_key_value_types(group, (('name', str), ('description', str)), verrors, f'{schema}.group.{index}')

    for index, portal_details in enumerate((questions_config.get('portals') or {}).items()):
        portal_type, portal_schema = portal_details
        error_schema = f'{schema}.portals.{index}'
        if not isinstance(portal_type, str):
            verrors.add(error_schema, 'Portal type must be a string')
        if not isinstance(portal_schema, dict):
            verrors.add(error_schema, 'Portal schema must be a dictionary')
        else:
            validate_key_value_types(
                portal_schema, (('protocols', list), ('host', list), ('ports', list), ('path', str, False)),
                verrors, error_schema
            )

    validate_variable_uniqueness(questions_config['questions'], f'{schema}.questions', verrors)
    for index, question in enumerate(questions_config['questions']):
        validate_question(question, f'{schema}.questions.{index}', verrors, (('group', str),))
        if question.get('group') and question['group'] not in groups:
            verrors.add(f'{schema}.questions.{index}.group', f'Please specify a group declared in "{schema}.groups"')

    if questions_config.get(CUSTOM_PORTALS_ENABLE_KEY):
        if not questions_config.get(CUSTOM_PORTAL_GROUP_KEY):
            verrors.add(
                f'{schema}.{CUSTOM_PORTALS_ENABLE_KEY}',
                f'{CUSTOM_PORTAL_GROUP_KEY!r} must be specified when user specified portals are desired'
            )
        elif questions_config[CUSTOM_PORTAL_GROUP_KEY] not in groups:
            verrors.add(
                f'{schema}.{CUSTOM_PORTAL_GROUP_KEY}',
                'Specified group not declared under "groups"'
            )

    verrors.check()


def validate_question(
    question_data: dict, schema: str, verrors: ValidationErrors, validate_top_level_attrs: typing.Optional[tuple] = None
):
    if not isinstance(question_data, dict):
        verrors.add(schema, 'Question must be a valid dictionary.')
        return

    validate_top_level_attrs = validate_top_level_attrs or tuple()
    validate_key_value_types(
        question_data, (('variable', str), ('label', str), ('schema', dict)) + validate_top_level_attrs, verrors, schema
    )
    if type(question_data.get('schema')) != dict:
        return

    if question_data['variable'] == CUSTOM_PORTALS_KEY:
        verrors.add(
            f'{schema}.variable',
            f'{CUSTOM_PORTALS_KEY!r} is a reserved variable name and cannot be specified by app developer'
        )
        # No need to validate the question data etc here
        return

    try:
        Variable(question_data).validate(schema)
    except ValidationErrors as ve:
        verrors.extend(ve)
        return

    schema_data = question_data['schema']
    variable_type = schema_data['type']

    for condition, key, schema_str in (
        (variable_type != 'list', 'subquestions', f'{schema}.schema.subquestions'),
        (variable_type == 'list', 'items', f'{schema}.schema.items'),
        (variable_type == 'dict', 'attrs', f'{schema}.schema.attrs'),
    ):
        if not (condition and type(schema_data.get(key)) == list):
            continue

        if variable_type == 'dict':
            validate_variable_uniqueness(schema_data[key], f'{schema}.{schema_str}', verrors)

        for index, item in enumerate(schema_data[key]):
            validate_question(item, f'{schema_str}.{index}', verrors)


def validate_variable_uniqueness(data: dict, schema: str, verrors: ValidationErrors):
    variables = []
    for index, question in enumerate(data):
        if question['variable'] in variables:
            verrors.add(
                f'{schema}.{index}', f'Variable name {question["variable"]!r} has been used again which is not allowed'
            )
        else:
            variables.append(question['variable'])
            sub_questions = question.get('subquestions') or []
            for sub_index, sub_question in enumerate(sub_questions):
                if sub_question['variable'] in variables:
                    verrors.add(
                        f'{schema}.{index}.subquestions.{sub_index}',
                        f'Variable name {sub_question["variable"]!r} has been used again which is not allowed'
                    )
                else:
                    variables.append(sub_question['variable'])

    verrors.check()
