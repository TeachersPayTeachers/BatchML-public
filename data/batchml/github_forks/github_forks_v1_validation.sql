WITH prod_metrics AS (
    SELECT AVG(predicted_repository_forks) AS prod_avg,
        STDDEV(predicted_repository_forks) AS prod_sd,
        COUNT(*) AS prod_ct
    FROM {{target_dataset}}.github_forks_v1_preds_prod
)

SELECT
    AVG(predicted_repository_forks) BETWEEN 40 AND 60 AS average_in_range,
    STDDEV(predicted_repository_forks) BETWEEN 40 AND 100 AS stddev_in_range,
    COUNT(*) BETWEEN 6000000 AND 7000000 AS count_in_range,
    ABS(AVG(predicted_repository_forks) - (SELECT prod_avg FROM prod_metrics)) < 1.0 AS avg_moved_little,
    ABS(STDDEV(predicted_repository_forks) - (SELECT prod_sd FROM prod_metrics)) < 1.0 AS sd_moved_little
FROM {{target_dataset}}.github_forks_v1_preds_staging;
