[BatchML](https://github.com/TeachersPayTeachers/BatchML-public) was developed by 
[Teachers Pay Teachers](https://www.teacherspayteachers.com/Careers) (TPT)
as a lightweight system for quickly building predictive models, leveraging:

* [Google Cloud BigQuery](https://cloud.google.com/bigquery)
* [dbt](http://getdbt.com)-based Data Warehouse
* [Google Cloud Composer](https://cloud.google.com/composer) ([Airflow](https://airflow.apache.org/))
* [Google Cloud BigQuery ML](https://cloud.google.com/bigquery-ml/docs?hl=en)
* [Google Cloud Build](https://cloud.google.com/build?hl=en)
* [Google Cloud Monitoring](https://cloud.google.com/monitoring) and Alerting

Typical use-cases are annotating major entities (users, items, sales leads, etc.) with daily predictions
or inferences, for operational or analytical use.

This README contains:

* Steps to set up Google Cloud resources to build and deploy an example model.
* Local development setup steps.
* Standard workflow for new-model development in this repo.

## Authors/Contributors:

* [Harlan Harris](https://github.com/harlanh)
* [Grayson Williams](https://github.com/grayson-tpt)

See also `CONTRIBUTING.md`.

## Alternatives & Prior Art

* It's easy enough to schedule SQL queries, including BigQuery ML queries, in BigQuery, but with much less 
safety for production use-cases.
* You can certainly manually create Airflow DAGs -- this system just removes the need to write Python code, 
and makes common cases much easier.
* The [dbt_ml](https://hub.getdbt.com/kristeligt-dagblad/dbt_ml/latest/) extension to 
[dbt](http://getdbt.com) lets you include BigQuery ML predictions in your DBT DAG. It has many
common motivations to this system, and you should definitely consider it if you're considering this.
* Commercial tools such as [Continual](https://continual.ai/) offer nice interfaces for solving related problems.
* Google Cloud's [Vertex AI](https://cloud.google.com/vertex-ai) suite provides tools for building predictive models, including workflow
tools. It's best suited for deployment and monitoring of real-time APIs. Note that there is expected to
be some convergence between BigQuery ML and Vertex AI over time.
* If your data is in the AWS or Azure stacks, AWS and Azure have lots of tools that are similar to Google Cloud's. This tool probably isn't that helpful, in that case.
* The use of YAML and Jinja templating is of course inspired by the [dbt](http://getdbt.com) design.

## Status and License

TPT uses this framework in production; you should do so with caution and assume that there
are bugs.

See `LICENSE.md` for the standard MIT license.

# Example Setup

The following steps are needed to get the sample model in this repo running. 

Note that this does not include the steps for local development and iteration from a laptop.
See the section below for information on how to do that.

## Google Cloud

* https://console.cloud.google.com/getting-started
* Create a new project, or select an existing one.
* Add or create a Billing Account, and link it to your project.

## Fork the Repo

You're going to want to use your own copy of this repo, so that you can add to it, do local development, etc!

## Composer

[Composer](https://cloud.google.com/composer) is the name used by GCP for it's managed [Airflow](https://airflow.apache.org/) service. Airflow is an open source scheduling and workflow orchestration
framework written in Python. BatchML is a system for creating Airflow DAGs.

For a real project, you probably want to set up two Composer environments, one for test, and one for prod.
For now, just set up a single environment.

* https://console.cloud.google.com/composer will redirect you to a page where you can enable Composer. Do so.
(It takes a few minutes.)
* Create a Composer 2 environment. You must call it `batchml-prod`, for the Deploy step below to work. 
* You can mostly stick with the defaults. You definitely only need a Small environment. 
* For the purposes of this demo, use `US` as the location. If you change it, you'll also need to change the location in `cloudbuild.yaml`.
* (It takes around 15 minutes to come up.)
* Once the Composer cluster is up, there should be a link to the "Airflow webserver". You can click the link 
to see just the default `airflow_monitoring` DAG, which should be running successfully.
* Open the Compose environment you just created, click on Environment Variables, and add two variables:
  * `COMPOSER_LOCAL_STORAGE` : `/home/airflow/gcs`
  * `AIRFLOW_ENVIRONMENT`: `prod`

## Build

For a real project, you probably sent to set up two Build Triggers -- one for the test environment and one for
prod. It's handy to have the test environment build and deploy with every commit. The prod environment should
look like the below -- require a manual button-push to deploy the `main` branch.

* Set up a Trigger at https://console.cloud.google.com/cloud-build/triggers/add . Give it a name like
`deploy-batchml-main`. 
* The Event should be "Manual invocation". 
* Connect a new repository, and point it at
your fork of this repo (you may need to give Google Cloud Build access to the repository as part of the
auth flow). 
* The Configuration defaults (use `cloudbuild.yaml` in the repo) should work.
* Add a Substitution Variable called `_AIRFLOW_ENVIRONMENT` with value `prod`.
* Save it.

Now, give Build permissions to push to Composer and Google Cloud Storage.

* Open https://console.cloud.google.com/iam-admin/iam .
* Find the Principal with domain `cloudbuild.gserviceaccount.com`. It should have "Cloud Build Service Account"
already. Edit it, and add "Composer Worker".

## Deploy

* In the Cloud Build console, click "Run" to start the test, build, and deploy process. It takes about 10
minutes, annoyingly.
* In the Airflow console, turn off the `archiving` and `v1_scoring` DAGs for `github_forks` for now. 
They'll fail if they run, because there's no model yet. (They probably failed already, as Airflow will try
to run everything with a schedule on first startup.)

## BigQuery Setup

* BigQuery needs a dataset to write the views, tables, and models to. The `prod` model is configured in
`batchml.yaml` to use `data_science`, so create a dataset with that name in your
[BigQuery](https://console.cloud.google.com/bigquery) project. Use `US` as a location and don't
expire tables.

## Train

* In the Airflow console, click the Play icon, then Trigger DAG on the `training` row to start it.

## Start Prediction

## Set Version

## Logging, Monitoring, and Alerting


# Local Development

