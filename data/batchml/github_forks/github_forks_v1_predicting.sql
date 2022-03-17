CREATE TABLE {{target_dataset}}.github_forks_v1_preds_staging AS
SELECT repository_url,
    predicted_repository_forks,
    CURRENT_TIMESTAMP() AS predicted_at     -- will be handy for archives
FROM ML.PREDICT(MODEL `{{target_dataset}}.github_forks_v1_model`,
    (
       SELECT * FROM `{{target_dataset}}.github_forks_v1_scoring`
    )
)
