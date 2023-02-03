import random
import re
import os
import string

from django.shortcuts import render
from google.cloud import bigquery
from google.cloud import datacatalog

PROJECT_ID = os.environ.get('PROJECT_ID', default='playground-jreimers')
BIGQUERY_TABLE_LINKED_RESOURCE_PATTERN = \
    re.compile(r'\/\/bigquery\.googleapis\.com\/projects\/(.*)\/datasets\/(.*)\/tables\/(.*)')


class DataCatalogTagField(object):

    def __init__(self, name, value):
        self.name = name
        self.value = value


class DataCatalogTag(object):

    def __init__(self, display_name, fields):
        self.display_name = display_name
        self.fields = fields


class DataCatalogBiqQueryTable(object):

    def __init__(self, datacatalog_entry, tags, table_project_id, table_dataset_id, table_id, data):
        self.datacatalog_entry = datacatalog_entry
        self.tags = tags
        self.table_project_id = table_project_id
        self.table_dataset_id = table_dataset_id
        self.table_id = table_id
        self.data = data


def index(request):
    datacatalog_client = datacatalog.DataCatalogClient()
    scope = datacatalog.SearchCatalogRequest.Scope()
    scope.include_project_ids.append(PROJECT_ID)

    query = 'system=bigquery type=table'
    # query = 'system=bigquery type=table tag:pii.has_pii=False'
    catalog_entries = datacatalog_client.search_catalog(scope=scope, query=query)
    tables = []
    bigquery_client = bigquery.Client(project=PROJECT_ID)
    for catalog_entry in catalog_entries:
        tags_request = datacatalog.ListTagsRequest(
            parent=catalog_entry.relative_resource_name
        )
        tags = datacatalog_client.list_tags(tags_request)
        view_tags = []
        for tag in tags:
            view_tag = DataCatalogTag(tag.template_display_name, [])
            for field in tag.fields.values():
                view_tag.fields += [field]
            view_tags += [view_tag]

        # BigQuery Data
        m = BIGQUERY_TABLE_LINKED_RESOURCE_PATTERN.match(catalog_entry.linked_resource)
        table_project_id, table_dataset_id, table_id = m.groups()
        job_config = bigquery.QueryJobConfig()
        job = bigquery_client.query(query=f"select * from {table_project_id}.{table_dataset_id}.{table_id}",
                                    job_config=job_config,
                                    job_id=f"job-{table_id}-{''.join(random.choices(string.ascii_lowercase, k=10))}")
        data = job.result().to_dataframe()

        tables += [DataCatalogBiqQueryTable(catalog_entry, view_tags, table_project_id, table_dataset_id, table_id, data)]

    context = {'tables': tables}
    return render(request, 'data.html', context)
