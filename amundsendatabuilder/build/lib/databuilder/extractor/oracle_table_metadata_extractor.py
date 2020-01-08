import logging
from collections import namedtuple

from pyhocon import ConfigFactory, ConfigTree  # noqa: F401
from typing import Iterator, Union, Dict, Any  # noqa: F401

from databuilder import Scoped
from databuilder.extractor.base_extractor import Extractor
from databuilder.extractor.sql_alchemy_extractor import SQLAlchemyExtractor
from databuilder.models.table_metadata import TableMetadata, ColumnMetadata
from itertools import groupby


TableKey = namedtuple('TableKey', ['schema_name', 'table_name'])

LOGGER = logging.getLogger(__name__)


class OracleTableMetadataExtractor(Extractor):
    """
    Extracts Hive table and column metadata from underlying meta store database using SQLAlchemyExtractor
    """
    # SELECT statement from hive metastore database to extract table and column metadata
    # Below SELECT statement uses UNION to combining two queries together.
    # 1st query is retrieving partition columns
    # 2nd query is retrieving columns
    # Using UNION to combine above two statements and order by table & partition identifier.
    SQL_STATEMENT = """
    SELECT ucc.COLUMN_NAME as name, ucc.COMMENTS as description, utc.DATA_TYPE as Col_Type,utc.COLUMN_ID as sort_order,'oracle' as database,at.OWNER as schema_name, 
utb.TABLE_NAME as table_name, utb.COMMENTS as table_desc
    
    FROM
    user_tab_comments utb
    LEFT JOIN user_col_comments ucc ON
    utb.TABLE_NAME = ucc.TABLE_NAME
    LEFT JOIN user_tab_columns utc ON
    utc.TABLE_NAME = utb.TABLE_NAME
    LEFT JOIN ALL_TABLES at ON
    at.TABLE_NAME = utb.TABLE_NAME 
     """


    # CONFIG KEYS
    WHERE_CLAUSE_SUFFIX_KEY = 'where_clause_suffix'
    CLUSTER_KEY = 'cluster'

    DEFAULT_CONFIG = ConfigFactory.from_dict({WHERE_CLAUSE_SUFFIX_KEY: ' ',
                                              CLUSTER_KEY: 'gold'})

    def init(self, conf):
        # type: (ConfigTree) -> None
        conf = conf.with_fallback(OracleTableMetadataExtractor.DEFAULT_CONFIG)
        self._cluster = '{}'.format(conf.get_string(OracleTableMetadataExtractor.CLUSTER_KEY))

        self.sql_stmt = OracleTableMetadataExtractor.SQL_STATEMENT.format(
            where_clause_suffix=conf.get_string(OracleTableMetadataExtractor.WHERE_CLAUSE_SUFFIX_KEY))

        LOGGER.info('SQL for Oracle: {}'.format(self.sql_stmt))

        self._alchemy_extractor = SQLAlchemyExtractor()
        sql_alch_conf = Scoped.get_scoped_conf(conf, self._alchemy_extractor.get_scope())\
            .with_fallback(ConfigFactory.from_dict({SQLAlchemyExtractor.EXTRACT_SQL: self.sql_stmt}))

        self._alchemy_extractor.init(sql_alch_conf)
        self._extract_iter = None  # type: Union[None, Iterator]

    def extract(self):
        # type: () -> Union[TableMetadata, None]
        if not self._extract_iter:
            self._extract_iter = self._get_extract_iter()
        try:
            return next(self._extract_iter)
        except StopIteration:
            return None

    def get_scope(self):
        # type: () -> str
        return 'extractor.oracle_table_metadata'

    def _get_extract_iter(self):
        # type: () -> Iterator[TableMetadata]
        """
        Using itertools.groupby and raw level iterator, it groups to table and yields TableMetadata
        :return:
        """
        for key, group in groupby(self._get_raw_extract_iter(), self._get_table_key):
            columns = []

            for row in group:
                last_row = row
                columns.append(ColumnMetadata(row['col_name'], row['col_description'],
                                              row['col_type'], row['col_sort_order']))

            yield TableMetadata(self._database,last_row['cluster'],
                                last_row['schema_name'],
                                last_row['name'],
                                last_row['description'],
                                columns)


    def _get_raw_extract_iter(self):
        # type: () -> Iterator[Dict[str, Any]]
        """
        Provides iterator of result row from SQLAlchemy extractor
        :return:
        """
        row = self._alchemy_extractor.extract()
        while row:
            yield row
            row = self._alchemy_extractor.extract()

    def _get_table_key(self, row):
        # type: (Dict[str, Any]) -> Union[TableKey, None]
        """
        Table key consists of schema and table name
        :param row:
        :return:
        """
        if row:
            print(row['name'])
            return TableKey(schema_name=row["schema_name"], table_name=row['name'])

        return None

