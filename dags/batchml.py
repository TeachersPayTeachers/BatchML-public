from datetime import datetime, timedelta
import os
import yaml

from jinja2 import Template

from airflow.contrib.operators.bigquery_operator import BigQueryOperator
from airflow.contrib.operators.bigquery_check_operator import BigQueryCheckOperator
from airflow import DAG


def corsql(sql, tablename):
    # Create Or Replace View
    return f"CREATE OR REPLACE VIEW {tablename} AS {sql};"


def get_data_filename_path(fn):
    return os.path.join(os.environ.get("COMPOSER_LOCAL_STORAGE"), "data", "batchml", fn)


def get_sql(fn):
    with open(get_data_filename_path(fn), "r", encoding="utf8") as sql_file:
        sql = sql_file.read()
    return sql


# globals

airflow_environment = os.environ.get("AIRFLOW_ENVIRONMENT")

# generic SQL templates, not per-model
promote_sql_template = """
-- 1. point the production view at the staging table
-- 2. replace the production table with the staging table
-- 3. point the production view at the production table
-- 4. delete the staging table
-- There should be no gap in availability using this method.

CREATE OR REPLACE VIEW {{target_dataset}}.{{model_code}}_{{version_code}}_preds
AS
SELECT *
FROM {{target_dataset}}.{{model_code}}_{{version_code}}_preds_staging;

CREATE OR REPLACE TABLE {{target_dataset}}.{{model_code}}_{{version_code}}_preds_prod
AS
SELECT *
FROM {{target_dataset}}.{{model_code}}_{{version_code}}_preds_staging;

CREATE OR REPLACE VIEW {{target_dataset}}.{{model_code}}_{{version_code}}_preds
AS
SELECT *, "{{version_code}}" AS version
FROM {{target_dataset}}.{{model_code}}_{{version_code}}_preds_prod;

DROP TABLE {{target_dataset}}.{{model_code}}_{{version_code}}_preds_staging;
"""

# archive does not use versioning!
archive_sql_template = """
CREATE TABLE IF NOT EXISTS {{target_dataset}}.{{model_code}}_archive
PARTITION BY DATE_TRUNC(predicted_at, MONTH)
AS SELECT * FROM {{target_dataset}}.{{model_code}}_preds LIMIT 0;

INSERT {{target_dataset}}.{{model_code}}_archive
SELECT * FROM {{target_dataset}}.{{model_code}}_preds;
"""

force_prod_sql_template = """
CREATE TABLE IF NOT EXISTS {{target_dataset}}.{{model_code}}_{{version_code}}_preds_prod
AS SELECT * FROM {{target_dataset}}.{{model_code}}_{{version_code}}_preds_staging;
"""

# load the config file
with open(get_data_filename_path("batchml.yaml"), "r", encoding="utf8") as config_file:
    dag_config = yaml.safe_load(config_file)


# define functions to generate each DAG
def generate_scoring_dag(model_code, version_code, dag_id):
    # NOTE: if you change this here, also change it in `generate_training_dag` & `generate_archive_dag`!
    # environment-specific and model-specific over-rides global
    this_config = {
        **dag_config["global"],
        **dag_config[airflow_environment],
        **dag_config["models"][model_code],
        "model_code": model_code,
        "version_code": version_code,
        "environment": airflow_environment,
    }

    scoring_sql = Template(
        get_sql(f"{model_code}/{model_code}_{version_code}_scoring.sql")
    ).render(**this_config)
    validation_sql = Template(
        get_sql(f"{model_code}/{model_code}_{version_code}_validation.sql")
    ).render(**this_config)
    predict_sql = Template(
        get_sql(f"{model_code}/{model_code}_{version_code}_predicting.sql")
    ).render(**this_config)

    # standard steps
    promote_sql = Template(promote_sql_template).render(**this_config)
    force_prod_sql = Template(force_prod_sql_template).render(**this_config)

    ### Scoring DAG
    with DAG(
        dag_id=dag_id,
        start_date=datetime(2021, 12, 10),
        catchup=False,
        schedule_interval=this_config["schedule"],
        default_args={
            "owner": "data-science",
            "retries": 1,
            "retry_delay": timedelta(seconds=60),
            "depends_on_past": False,
        },
        concurrency=1,
        max_active_runs=1,
    ) as dag_scoring:
        # Ensure a view exists for scoring to run
        cor_view_scoring_task = BigQueryOperator(
            task_id="corv_scoring",
            sql=corsql(
                scoring_sql,
                f"{this_config['target_dataset']}.{model_code}_{version_code}_scoring",
            ),
            use_legacy_sql=False,
        )

        # Actually do the scoring into a staging table
        scoring_task = BigQueryOperator(
            task_id="scoring",
            sql=predict_sql,
            use_legacy_sql=False,
        )

        # If the prod table doesn't exist, create it, so validation will run
        # (If it does exist, do nothing!)
        force_prod_task = BigQueryOperator(
            task_id="force_prod", sql=force_prod_sql, use_legacy_sql=False
        )

        # Validate the predictions, internally and vs. prod table
        validation_task = BigQueryCheckOperator(
            task_id="validation", sql=validation_sql, use_legacy_sql=False
        )

        # Promote staging to prod
        promotion_task = BigQueryOperator(
            task_id="promotion", sql=promote_sql, use_legacy_sql=False
        )

        # pylint: disable=pointless-statement
        cor_view_scoring_task >> scoring_task >> force_prod_task >> validation_task >> promotion_task

    return dag_scoring


def generate_archive_dag(model_code, dag_id):
    this_config = {
        **dag_config["global"],
        **dag_config[airflow_environment],
        **dag_config["models"][model_code],
        "model_code": model_code,
        "environment": airflow_environment,
    }

    archive_sql = Template(archive_sql_template).render(**this_config)

    with DAG(
        dag_id=dag_id,
        start_date=datetime(2021, 12, 10),
        catchup=False,
        schedule_interval=this_config["archive_schedule"],
        default_args={
            "owner": "data-science",
            "retries": 1,
            "retry_delay": timedelta(seconds=60),
            "depends_on_past": False,
        },
        concurrency=1,
        max_active_runs=1,
    ) as dag_archive:
        # Append to an archive table
        archive_task = BigQueryOperator(
            task_id="archive", sql=archive_sql, use_legacy_sql=False
        )

        # pylint: disable=pointless-statement
        archive_task

    return dag_archive


def generate_training_dag(model_code, version_code, dag_id):
    # environment-specific and model-specific over-rides global
    this_config = {
        **dag_config["global"],
        **dag_config[airflow_environment],
        **dag_config["models"][model_code],
        "model_code": model_code,
        "version_code": version_code,
        "environment": airflow_environment,
    }

    training_sql = Template(
        get_sql(f"{model_code}/{model_code}_{version_code}_training.sql")
    ).render(**this_config)
    train_model_sql = Template(
        get_sql(f"{model_code}/{model_code}_{version_code}_train_model.sql")
    ).render(**this_config)

    ### Training DAG
    with DAG(
        dag_id=dag_id,
        start_date=datetime(2021, 12, 10),
        catchup=False,
        schedule_interval=None,
        default_args={
            "owner": "data-science",
            "retries": 1,
            "retry_delay": timedelta(seconds=60),
            "depends_on_past": False,
        },
        concurrency=1,
        max_active_runs=1,
    ) as dag_training:
        cor_view_training_task = BigQueryOperator(
            task_id="corv_training",
            sql=corsql(
                training_sql,
                f"{this_config['target_dataset']}.{model_code}_{version_code}_training",
            ),
            use_legacy_sql=False,
        )

        train_model_task = BigQueryOperator(
            task_id="train", sql=train_model_sql, use_legacy_sql=False
        )

        # pylint: disable=pointless-statement
        cor_view_training_task >> train_model_task

    return dag_training


# loop through the models in the config file
for model_key in dag_config["models"].keys():
    for version_key in dag_config["models"][model_key]["versions"]:
        training_dag_id = f"{model_key}_{version_key}_training"
        globals()[training_dag_id] = generate_training_dag(
            model_key, version_key, training_dag_id
        )

        scoring_dag_id = f"{model_key}_{version_key}_scoring"
        globals()[scoring_dag_id] = generate_scoring_dag(
            model_key, version_key, scoring_dag_id
        )

    archive_dag_id = f"{model_key}_archiving"
    globals()[archive_dag_id] = generate_archive_dag(model_key, archive_dag_id)
