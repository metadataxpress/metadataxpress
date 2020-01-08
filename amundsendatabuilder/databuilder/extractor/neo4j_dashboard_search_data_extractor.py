import textwrap
from typing import Any  # noqa: F401

from pyhocon import ConfigTree  # noqa: F401

from amundsendatabuilder.databuilder import Scoped
from amundsendatabuilder.databuilder.extractor.base_extractor import Extractor
from amundsendatabuilder.databuilder.extractor.neo4j_extractor import Neo4jExtractor
from amundsendatabuilder.databuilder.publisher.neo4j_csv_publisher import JOB_PUBLISH_TAG


class Neo4jDashboardSearchDataExtractor(Extractor):
    """
    Extractor to fetch data required to support search from Neo4j graph database
    Use Neo4jExtractor extractor class
    """
    CYPHER_QUERY_CONFIG_KEY = 'cypher_query'

    DEFAULT_NEO4J_CYPHER_QUERY = textwrap.dedent(
        """
     MATCH (d)-[:DESCRIPTION]->(ddesc:Description)
OPTIONAL MATCH (d)-[:OWNER]->(owner:Schema)
OPTIONAL MATCH (d)-[:DASHBOARD_OF]->(dgroup:Dashboardgroup)
OPTIONAL MATCH (d)-[:DATABASE]->(dbase:Database)
OPTIONAL MATCH (d)-[:NAME]->(dname:Name)
OPTIONAL MATCH (d)-[:COLUMN_NAMES]->(dcol:Tag)
RETURN ddesc.description as description,owner.schema_name AS schema_name,
dgroup.dashboard AS dashboard_group,d.dashboard AS dashboard_name,
dbase.database AS database,dname.name AS name,dcol.key AS column_names;
        """
    )

    def init(self, conf):
        # type: (ConfigTree) -> None
        """
        Initialize Neo4jExtractor object from configuration and use that for extraction
        """
        self.conf = conf

        # extract cypher query from conf, if specified, else use default query
        if Neo4jDashboardSearchDataExtractor.CYPHER_QUERY_CONFIG_KEY in conf:
            self.cypher_query = conf.get_string(Neo4jDashboardSearchDataExtractor.CYPHER_QUERY_CONFIG_KEY)
        else:
            self.cypher_query = self._add_publish_tag_filter(conf.get_string(JOB_PUBLISH_TAG, ''),
                                                             Neo4jDashboardSearchDataExtractor.
                                                             DEFAULT_NEO4J_CYPHER_QUERY)

        self.neo4j_extractor = Neo4jExtractor()
        # write the cypher query in configs in Neo4jExtractor scope
        key = self.neo4j_extractor.get_scope() + '.' + Neo4jExtractor.CYPHER_QUERY_CONFIG_KEY
        self.conf.put(key, self.cypher_query)
        # initialize neo4j_extractor from configs
        self.neo4j_extractor.init(Scoped.get_scoped_conf(self.conf, self.neo4j_extractor.get_scope()))

    def close(self):
        # type: () -> None
        """
        Use close() method specified by neo4j_extractor
        to close connection to neo4j cluster
        """
        self.neo4j_extractor.close()

    def extract(self):
        # type: () -> Any
        """
        Invoke extract() method defined by neo4j_extractor
        """
        return self.neo4j_extractor.extract()

    def get_scope(self):
        # type: () -> str
        return 'extractor.dashboard_search_data'

    def _add_publish_tag_filter(self, publish_tag, cypher_query):
        """
        Adds publish tag filter into Cypher query
        :param publish_tag: value of publish tag.
        :param cypher_query:
        :return:
        """
        if not publish_tag:
            publish_tag_filter = ''
        else:
            publish_tag_filter = """WHERE dashboard.published_tag = '{}'""".format(publish_tag)

        return cypher_query.format(publish_tag_filter=publish_tag_filter)
