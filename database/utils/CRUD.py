from typing import Dict, List, TypeVar, Any
from peewee import ModelSelect
from database.common.models import ModelBase, db

T = TypeVar("T")


def _store_data(db: db, model: T, *data: List[Dict]) -> None:
    with db.atomic():
        model.insert_many(*data).execute()


def _retrieve_all_data(db: db, model: T, *columns: ModelBase) -> ModelSelect:
    with db.atomic():
        response = model.select(*columns)
    return response


def _check_if_data_exists(sdb: db, model: T, *query: Any, **filters: Any) -> bool:
    exists = True
    try:
        with sdb.atomic():
            instance = model.get_or_none(*query, **filters)
            if instance is None:
                exists = False
    except model.DoesNotExist:
        exists = False
    return exists


class CRUDInterface:

    @staticmethod
    def create():
        return _store_data

    @staticmethod
    def retrieve():
        return _retrieve_all_data

    @staticmethod
    def check_exists():
        return _check_if_data_exists

if __name__ == "__main__":
    CRUDInterface()
