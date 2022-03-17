CREATE OR REPLACE MODEL {{target_dataset}}.github_forks_v1_model
OPTIONS(MODEL_TYPE = 'LINEAR_REG',
   INPUT_LABEL_COLS = ['repository_forks']) AS
SELECT * FROM {{target_dataset}}.github_forks_v1_training;
