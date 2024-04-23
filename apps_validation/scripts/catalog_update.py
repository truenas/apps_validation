import typing

from apps_validation.catalog_reader.catalog import retrieve_train_names, retrieve_trains_data, get_apps_in_trains


def get_trains(location: str) -> typing.Tuple[dict, dict]:
    preferred_trains: list = []
    trains_to_traverse = retrieve_train_names(location)
    catalog_data = {}
    versions_data = {}
    for train_name, train_data in retrieve_trains_data(
        get_apps_in_trains(trains_to_traverse, location), location, preferred_trains, trains_to_traverse
    )[0].items():
        catalog_data[train_name] = {}
        versions_data[train_name] = {}
        for app_name, app_data in train_data.items():
            catalog_data[train_name][app_name] = {}
            versions_data[train_name][app_name] = {}
            for k, v in app_data.items():
                if k == 'versions':
                    versions_data[train_name][app_name][k] = v
                else:
                    catalog_data[train_name][app_name][k] = v

    return catalog_data, versions_data
