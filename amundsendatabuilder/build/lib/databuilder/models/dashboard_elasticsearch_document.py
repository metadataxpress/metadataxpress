from typing import List, Optional  # noqa: F401

from databuilder.models.elasticsearch_document import ElasticsearchDocument


class DashboardESDocument(ElasticsearchDocument):
    """
    Schema for the Search index document
    """
    def __init__(self,
                 dashboard_group,  # type: str
                 dashboard_name,  # type: str
                 description,  # type: Union[str, None]
                 name,  # type: str
                 user_id,  # type: str
                 user_name,  # type: str
                 tags  # type: list
                 ):
        # type: (...) -> None
        self.dashboard_group = dashboard_group
        self.dashboard_name = dashboard_name
        self.description = description
        self.name = name
        self.user_id = user_id
        self.user_name = user_name
        self.tags = tags
