from collections import namedtuple

from typing import Iterable, Any, Union, Iterator, Dict, Set  # noqa: F401

# TODO: We could separate TagMetadata from table_metadata to own module
from amundsendatabuilder.databuilder.models.table_metadata import TagMetadata
from amundsendatabuilder.databuilder.models.neo4j_csv_serde import (
    Neo4jCsvSerializable, NODE_LABEL, NODE_KEY, RELATION_START_KEY, RELATION_END_KEY, RELATION_START_LABEL,
    RELATION_END_LABEL, RELATION_TYPE, RELATION_REVERSE_TYPE)


NodeTuple = namedtuple('KeyName', ['key', 'name', 'label'])
RelTuple = namedtuple('RelKeys', ['start_label', 'end_label', 'start_key', 'end_key', 'type', 'reverse_type'])


class DashboardMetadata(Neo4jCsvSerializable):
    """
    Dashboard metadata that contains dashboardgroup, tags, description, userid and lastreloadtime.
    It implements Neo4jCsvSerializable so that it can be serialized to produce
    Dashboard, Tag, Description, Lastreloadtime and relation of those. Additionally, it will create
    Dashboardgroup with relationships to Dashboard. If users exist in neo4j, it will create
    the relation between dashboard and user (owner).
    Lastreloadtime is the time when the Dashboard was last reloaded.
    """
    DASHBOARD_NODE_LABEL = 'Dashboard'
    DASHBOARD_KEY_FORMAT = '{dashboard_group}://{dashboard_name}'
    DASHBOARD_NAME = 'dashboard'

    DASHBOARD_DESCRIPTION_NODE_LABEL = 'Description'
    DASHBOARD_DESCRIPTION = 'description'
    DASHBOARD_DESCRIPTION_FORMAT = '{dashboard_group}://{dashboard_name}/_description'
    DASHBOARD_DESCRIPTION_RELATION_TYPE = 'DESCRIPTION'
    DESCRIPTION_DASHBOARD_RELATION_TYPE = 'DESCRIPTION_OF'

    DASHBOARD_GROUP_NODE_LABEL = 'Dashboardgroup'
    DASHBOARD_GROUP_KEY_FORMAT = 'dashboardgroup://{dashboard_group}'
    DASHBOARD_GROUP_DASHBOARD_RELATION_TYPE = 'DASHBOARD'
    DASHBOARD_DASHBOARD_GROUP_RELATION_TYPE = 'DASHBOARD_OF'

    DASHBOARD_LAST_RELOAD_TIME_NODE_LABEL = 'Name'
    DASHBOARD_LAST_RELOAD_TIME = 'name'
    DASHBOARD_LAST_RELOAD_TIME_FORMAT = '{dashboard_group}://{dashboard_name}/_name'
    DASHBOARD_LAST_RELOAD_TIME_RELATION_TYPE = 'NAME'
    LAST_RELOAD_TIME_DASHBOARD_RELATION_TYPE = 'NAME_OF'

    DATABASE_NODE_LABEL = 'Database'
    DATABASE_KEY_FORMAT = 'database'
    DASHBOARD_DATABASE_RELATION_TYPE = "DATABASE"
    DATABASE_DASHBOARD_RELATION_TYPE = 'DATABASE_OF'


    OWNER_NODE_LABEL = 'Schema'
    OWNER_KEY_FORMAT = 'schema_name'
    DASHBOARD_OWNER_RELATION_TYPE = 'OWNER'
    OWNER_DASHBOARD_RELATION_TYPE = 'OWNER_OF'
    OWNER_ID = 'schema_name'

    DASHBOARD_TAG_RELATION_TYPE = 'COLUMN_NAMES'
    TAG_DASHBOARD_RELATION_TYPE = 'COLUMN_NAMES_OF'

    serialized_nodes = set()  # type: Set[Any]
    serialized_rels = set()  # type: Set[Any]

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
        self._node_iterator = self._create_next_node()
        self._relation_iterator = self._create_next_relation()

    def __repr__(self):
        # type: () -> str
        return 'DashboardMetadata({!r}, {!r}, {!r}, {!r}, {!r}, {!r}, {!r}, {!r}' \
            .format(self.database,
                    self.dashboard_group,
                    self.dashboard_name,
                    self.description,
                    self.name,
                    self.schema_name,
                    self.column_names
                    )

    def _get_dashboard_key(self):
        # type: () -> str
        return DashboardMetadata.DASHBOARD_KEY_FORMAT.format(dashboard_group=self.dashboard_group,
                                                             dashboard_name=self.dashboard_name)

    def _get_dashboard_description_key(self):
        # type: () -> str
        return DashboardMetadata.DASHBOARD_DESCRIPTION_FORMAT.format(dashboard_group=self.dashboard_group,
                                                                     dashboard_name=self.dashboard_name)

    def _get_dashboard_group_key(self):
        # type: () -> str
        return DashboardMetadata.DASHBOARD_GROUP_KEY_FORMAT.format(dashboard_group=self.dashboard_group)

    def _get_dashboard_last_reload_time_key(self):
        # type: () -> str
        return DashboardMetadata.DASHBOARD_LAST_RELOAD_TIME_FORMAT.format(dashboard_group=self.dashboard_group,
                                                                          dashboard_name=self.dashboard_name)

    def _get_dashboard_database_key(self):
        # type: () -> str
        return DashboardMetadata.DATABASE_KEY_FORMAT.format(database=self.database)

    def _get_owner_key(self):
        # type: () -> str
        return DashboardMetadata.OWNER_KEY_FORMAT.format(schema_name=self.schema_name)

    def create_next_node(self):
        # type: () -> Union[Dict[str, Any], None]
        try:
            return next(self._node_iterator)
        except StopIteration:
            return None

    def _create_next_node(self):
        # type: () -> Iterator[Any]
        # Dashboard node
        yield {NODE_LABEL: DashboardMetadata.DASHBOARD_NODE_LABEL,
               NODE_KEY: self._get_dashboard_key(),
               DashboardMetadata.DASHBOARD_NAME: self.dashboard_name,
               }

        # Dashboard group
        if self.dashboard_group:
            yield {NODE_LABEL: DashboardMetadata.DASHBOARD_GROUP_NODE_LABEL,
                   NODE_KEY: self._get_dashboard_group_key(),
                   DashboardMetadata.DASHBOARD_NAME: self.dashboard_group,
                   }

        # Database
        if self.database:
            yield {NODE_LABEL: DashboardMetadata.DATABASE_NODE_LABEL,
                   NODE_KEY: self._get_dashboard_database_key(),
                   DashboardMetadata.DATABASE_KEY_FORMAT: self.database,
                   }

        # Dashboard description node
        if self.description:
            yield {NODE_LABEL: DashboardMetadata.DASHBOARD_DESCRIPTION_NODE_LABEL,
                   NODE_KEY: self._get_dashboard_description_key(),
                   DashboardMetadata.DASHBOARD_DESCRIPTION: self.description}

        # Dashboard last reload time node
        if self.name:
            yield {NODE_LABEL: DashboardMetadata.DASHBOARD_LAST_RELOAD_TIME_NODE_LABEL,
                   NODE_KEY: self._get_dashboard_last_reload_time_key(),
                   DashboardMetadata.DASHBOARD_LAST_RELOAD_TIME: self.name}

        # Owner
        if self.schema_name:
            yield {NODE_LABEL: DashboardMetadata.OWNER_NODE_LABEL,
                   NODE_KEY: self._get_owner_key(),
                   DashboardMetadata.OWNER_KEY_FORMAT: self.schema_name}

    # Dashboard tag node
        if self.column_names:
            for tag in self.column_names:
                yield {NODE_LABEL: TagMetadata.TAG_NODE_LABEL,
                       NODE_KEY: TagMetadata.get_tag_key(tag),
                       TagMetadata.TAG_TYPE: 'dashboard'}

    def create_next_relation(self):
        # type: () -> Union[Dict[str, Any], None]
        try:
            return next(self._relation_iterator)
        except StopIteration:
            return None

    def _create_next_relation(self):
        # type: () -> Iterator[Any]

        # Dashboard group > Dashboard relation
        yield {
            RELATION_START_LABEL: DashboardMetadata.DASHBOARD_NODE_LABEL,
            RELATION_END_LABEL: DashboardMetadata.DASHBOARD_GROUP_NODE_LABEL,
            RELATION_START_KEY: self._get_dashboard_key(),
            RELATION_END_KEY: self._get_dashboard_group_key(),
            RELATION_TYPE: DashboardMetadata.DASHBOARD_DASHBOARD_GROUP_RELATION_TYPE,
            RELATION_REVERSE_TYPE: DashboardMetadata.DASHBOARD_GROUP_DASHBOARD_RELATION_TYPE
        }

        # Dashboard > Dashboard description relation
        if self.description:
            yield {
                RELATION_START_LABEL: DashboardMetadata.DASHBOARD_NODE_LABEL,
                RELATION_END_LABEL: DashboardMetadata.DASHBOARD_DESCRIPTION_NODE_LABEL,
                RELATION_START_KEY: self._get_dashboard_key(),
                RELATION_END_KEY: self._get_dashboard_description_key(),
                RELATION_TYPE: DashboardMetadata.DASHBOARD_DESCRIPTION_RELATION_TYPE,
                RELATION_REVERSE_TYPE: DashboardMetadata.DESCRIPTION_DASHBOARD_RELATION_TYPE
            }

        if self.database:
            yield {
                RELATION_START_LABEL: DashboardMetadata.DASHBOARD_NODE_LABEL,
                RELATION_END_LABEL: DashboardMetadata.DATABASE_NODE_LABEL,
                RELATION_START_KEY: self._get_dashboard_key(),
                RELATION_END_KEY: self._get_dashboard_database_key(),
                RELATION_TYPE: DashboardMetadata.DASHBOARD_DATABASE_RELATION_TYPE,
                RELATION_REVERSE_TYPE: DashboardMetadata.DATABASE_DASHBOARD_RELATION_TYPE
            }
        # Dashboard > Dashboard last reload time relation
        if self.name:
            yield {
                RELATION_START_LABEL: DashboardMetadata.DASHBOARD_NODE_LABEL,
                RELATION_END_LABEL: DashboardMetadata.DASHBOARD_LAST_RELOAD_TIME_NODE_LABEL,
                RELATION_START_KEY: self._get_dashboard_key(),
                RELATION_END_KEY: self._get_dashboard_last_reload_time_key(),
                RELATION_TYPE: DashboardMetadata.DASHBOARD_LAST_RELOAD_TIME_RELATION_TYPE,
                RELATION_REVERSE_TYPE: DashboardMetadata.LAST_RELOAD_TIME_DASHBOARD_RELATION_TYPE
            }

        if self.schema_name:
            yield {
                RELATION_START_LABEL: DashboardMetadata.DASHBOARD_NODE_LABEL,
                RELATION_END_LABEL: DashboardMetadata.OWNER_NODE_LABEL,
                RELATION_START_KEY: self._get_dashboard_key(),
                RELATION_END_KEY: self._get_owner_key(),
                RELATION_TYPE: DashboardMetadata.DASHBOARD_OWNER_RELATION_TYPE,
                RELATION_REVERSE_TYPE: DashboardMetadata.OWNER_DASHBOARD_RELATION_TYPE
            }
        # Dashboard > Dashboard tag relation
        if self.column_names:
            for tag in self.column_names:
                yield {
                    RELATION_START_LABEL: DashboardMetadata.DASHBOARD_NODE_LABEL,
                    RELATION_END_LABEL: TagMetadata.TAG_NODE_LABEL,
                    RELATION_START_KEY: self._get_dashboard_key(),
                    RELATION_END_KEY: TagMetadata.get_tag_key(tag),
                    RELATION_TYPE: DashboardMetadata.DASHBOARD_TAG_RELATION_TYPE,
                    RELATION_REVERSE_TYPE: DashboardMetadata.TAG_DASHBOARD_RELATION_TYPE
                }
        # Dashboard > Dashboard owner relation
        others = [
            RelTuple(start_label=DashboardMetadata.DASHBOARD_NODE_LABEL,
                     end_label=DashboardMetadata.OWNER_NODE_LABEL,
                     start_key=self._get_dashboard_key(),
                     end_key=self._get_owner_key(),
                     type=DashboardMetadata.DASHBOARD_OWNER_RELATION_TYPE,
                     reverse_type=DashboardMetadata.OWNER_DASHBOARD_RELATION_TYPE)
        ]

        for rel_tuple in others:
            if rel_tuple not in DashboardMetadata.serialized_rels:
                DashboardMetadata.serialized_rels.add(rel_tuple)
                yield {
                    RELATION_START_LABEL: rel_tuple.start_label,
                    RELATION_END_LABEL: rel_tuple.end_label,
                    RELATION_START_KEY: rel_tuple.start_key,
                    RELATION_END_KEY: rel_tuple.end_key,
                    RELATION_TYPE: rel_tuple.type,
                    RELATION_REVERSE_TYPE: rel_tuple.reverse_type
                }
