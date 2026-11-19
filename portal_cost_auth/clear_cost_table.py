table_name = "prd.value_stream_monitoring.databricks_costs_daily"
staging_name = "prd.value_stream_monitoring.databricks_costs_staging"
delta_path = "abfss://refinedzone@dls2adseus2edhprd01.dfs.core.windows.net/value_stream_monitoring/databricks_costs_daily"
staging_path = "abfss://refinedzone@dls2adseus2edhprd01.dfs.core.windows.net/value_stream_monitoring/databricks_costs_staging"

tables_to_drop = [table_name, staging_name]
paths_to_clear = [delta_path, staging_path]

for tbl in tables_to_drop:
    spark.sql(f"DROP TABLE IF EXISTS {tbl}")

for path in paths_to_clear:
    dbutils.fs.rm(path, True)

print("Cleared:", tables_to_drop, paths_to_clear)