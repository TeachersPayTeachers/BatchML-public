SELECT
   COALESCE(repository_forks, 0) AS repository_forks, -- target
   LOG(1 + repository_size) AS log_repo_size,
   repository_has_wiki,
   repository_has_issues
FROM `bigquery-public-data.samples.github_timeline`