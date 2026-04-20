from pydantic import BaseModel
from pydantic.alias_generators import to_camel


class Item(BaseModel, alias_generator=to_camel, populate_by_name=True):
    id: str
    name: str
