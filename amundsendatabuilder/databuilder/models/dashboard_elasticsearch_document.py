from typing import List, Optional  # noqa: F401

from amundsendatabuilder.databuilder.models.elasticsearch_document import ElasticsearchDocument


class DashboardESDocument(ElasticsearchDocument):
    """
    Schema for the Search index document
    """
    def __init__(self,
                 database,  # type: str
                 schema_name,  # type: str
                 description,  # type: Union[str, None]
                 name,  # type: str
                 dashboard_name,  # type: str
                 dashboard_group,  # type: str
                 column_names  # type: list
                 ):
        # type: (...) -> None
        self.database = database
        self.schema_name = schema_name
        self.description = description
        self.name = name
        self.dashboard_name = dashboard_name
        self.dashboard_group = dashboard_group
        self.column_names = column_names
