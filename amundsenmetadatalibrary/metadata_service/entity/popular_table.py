import attr
from marshmallow_annotations.ext.attrs import AttrsSchema


@attr.s(auto_attribs=True, kw_only=True)
class PopularTable:
    database = attr.ib()
    cluster = attr.ib()
    schema = attr.ib()
    name = attr.ib()
    description = None


class PopularTableSchema(AttrsSchema):
    class Meta:
        target = PopularTable
        register_as_scheme = True
