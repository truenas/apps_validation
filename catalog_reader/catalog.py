import concurrent.futures
import functools
import os
import typing

from .app import get_app_details
from .app_utils import get_default_questions_context
from .train_utils import get_train_path, is_train_valid


def app_details(
    apps: dict, location: str, questions_context: typing.Optional[dict], app_key: str, normalize_questions: bool = True,
) -> dict:
    train = apps[app_key]
    app = app_key.removesuffix(f'_{train}')
    app_location = os.path.join(get_train_path(location), train, app)
    return get_app_details(
        app_location, questions_context, {'retrieve_versions': True, 'normalize_questions': normalize_questions},
    )


def retrieve_train_names(location: str, all_trains=True, trains_filter=None) -> list:
    train_names = []
    trains_filter = trains_filter or []
    for train in os.listdir(location):
        if not (all_trains or train in trains_filter) or not is_train_valid(train, os.path.join(location, train)):
            continue
        train_names.append(train)
    return train_names


def get_apps_in_trains(trains_to_traverse: list, catalog_location: str) -> dict:
    items = {}
    for train in trains_to_traverse:
        items.update({
            f'{i}_{train}': train for i in os.listdir(os.path.join(get_train_path(catalog_location), train))
            if os.path.isdir(os.path.join(get_train_path(catalog_location), train, i))
        })

    return items


def retrieve_trains_data(
    apps: dict, catalog_location: str, preferred_trains: list, trains_to_traverse: list, job: typing.Any = None,
    questions_context: typing.Optional[dict] = None, normalize_questions: bool = True,
) -> typing.Tuple[dict, set]:
    questions_context = questions_context or get_default_questions_context()
    trains = {
        'stable': {},
        **{k: {} for k in trains_to_traverse},
    }
    unhealthy_apps = set()

    total_apps = len(apps)
    with concurrent.futures.ProcessPoolExecutor(max_workers=(5 if total_apps > 10 else 2)) as exc:
        for index, result in enumerate(zip(apps, exc.map(
            functools.partial(app_details, apps, catalog_location, questions_context),
            apps, chunksize=(10 if total_apps > 10 else 5)
        ))):
            app_key = result[0]
            app_info = result[1]
            train = apps[app_key]
            app = app_key.removesuffix(f'_{train}')
            if job:
                job.set_progress(
                    int((index / total_apps) * 80) + 10,
                    f'Retrieved information of {app!r} item from {train!r} train'
                )
            trains[train][app] = app_info
            if train in preferred_trains and not trains[train][app]['healthy']:
                unhealthy_apps.add(f'{app} ({train} train)')

    return trains, unhealthy_apps
