# Django Data Catalog
A simple example demonstrating how to search Data Catalog for BigQuery tables and fetching business metadata (tags).
Also demonstrates how query data in BigQuery and rendered in a simple Django view.

## Running Locally
Install Python 3.9, if not already installed.

Create a virtual environment and install dependencies:
```shell
python3 -m venv env
source env/bin/activate

python3 -m pip install -r requirements.txt
```

Then run using:
```shell
export PROJECT_ID=<project-id>
python3 manage.py runserver
```

## Build for Cloud Run
Build using Cloud Build and build packs:
```shell
gcloud builds submit --pack image=gcr.io/$PROJECT_ID/datacatalog
```

