"""
This is a example script which demo how to load data into neo4j without using Airflow DAG.
"""
import logging
import os
from pyhocon import ConfigFactory

from amundsendatabuilder.databuilder.extractor.generic_extractor import GenericExtractor
from amundsendatabuilder.databuilder.job.job import DefaultJob
from amundsendatabuilder.databuilder.loader.file_system_neo4j_csv_loader import FsNeo4jCSVLoader
from amundsendatabuilder.databuilder.publisher import neo4j_csv_publisher
from amundsendatabuilder.databuilder.publisher.neo4j_csv_publisher import Neo4jCsvPublisher
from amundsendatabuilder.databuilder.task.task import DefaultTask

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

# set env NEO4J_HOST to override localhost
NEO4J_ENDPOINT = 'bolt://{}:7687'.format(os.getenv('NEO4J_HOST', 'localhost'))
neo4j_endpoint = NEO4J_ENDPOINT

neo4j_user = 'neo4j'
neo4j_password = 'test'

# Input example
input = [
    {'dashboard_name': 'Agent', 'dashboard_group': 'Product - Jobs.cz', 'description': 'description of Dash',
     'name': 'Agents', 'schema_name': 'ssrs','database' : 'ssrs',
     'column_names': ['test_tag', 'tag2']},
]


def create_dashboard_neo4j_job(**kwargs):

    tmp_folder = '/var/tmp/amundsen/table_metadata'
    node_files_folder = '{tmp_folder}/nodes/'.format(tmp_folder=tmp_folder)
    relationship_files_folder = '{tmp_folder}/relationships/'.format(tmp_folder=tmp_folder)

    job_config = ConfigFactory.from_dict({
        'extractor.generic.{}'.format(GenericExtractor.EXTRACTION_ITEMS):
            iter(input),
        'extractor.generic.{}'.format('model_class'):
            'amundsendatabuilder.databuilder.models.dashboard_metadata.DashboardMetadata',
        'loader.filesystem_csv_neo4j.{}'.format(FsNeo4jCSVLoader.NODE_DIR_PATH):
            node_files_folder,
        'loader.filesystem_csv_neo4j.{}'.format(FsNeo4jCSVLoader.RELATION_DIR_PATH):
            relationship_files_folder,
        'publisher.neo4j.{}'.format(neo4j_csv_publisher.NODE_FILES_DIR):
            node_files_folder,
        'publisher.neo4j.{}'.format(neo4j_csv_publisher.RELATION_FILES_DIR):
            relationship_files_folder,
        'publisher.neo4j.{}'.format(neo4j_csv_publisher.NEO4J_END_POINT_KEY):
            neo4j_endpoint,
        'publisher.neo4j.{}'.format(neo4j_csv_publisher.NEO4J_USER):
            neo4j_user,
        'publisher.neo4j.{}'.format(neo4j_csv_publisher.NEO4J_PASSWORD):
            neo4j_password,
        'publisher.neo4j.{}'.format(neo4j_csv_publisher.JOB_PUBLISH_TAG):
            'unique_tag',  # should use unique tag here like {ds}
    })
    job = DefaultJob(conf=job_config,
                     task=DefaultTask(extractor=GenericExtractor(), loader=FsNeo4jCSVLoader()),
                     publisher=Neo4jCsvPublisher())
    return job


if __name__ == "__main__":
    job = create_dashboard_neo4j_job()
    job.launch()
