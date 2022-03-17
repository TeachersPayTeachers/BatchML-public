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

The following steps are needed to get the sample model in this repo running:

## Google Cloud

setup billing

## Clone

the repo

## Composer

[Composer](https://cloud.google.com/composer) is the name used by GCP for it's managed [Airflow](https://airflow.apache.org/) service. Airflow is an open source scheduling and workflow orchestration
framework written in Python.

## Build

## Deploy

## Set Version

## Logging, Monitoring, and Alerting



