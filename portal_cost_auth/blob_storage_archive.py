import pyspark.sql.functions as F

file_name = "databricks_storage_cost_archive.csv"
date_col, meter_col, cost_col = "UsageDate", "Meter", "Cost"

source_path = f"abfss://databricks@sasscaleservesavecusprd.dfs.core.windows.net/{file_name}"
table_name = "prd.value_stream_monitoring.databricks_storage_costs_archive"
staging_name = "prd.value_stream_monitoring.databricks_storage_costs_archive_staging"
delta_path = "abfss://refinedzone@dls2adseus2edhprd01.dfs.core.windows.net/value_stream_monitoring/databricks_storage_costs_archive"
staging_path = "abfss://refinedzone@dls2adseus2edhprd01.dfs.core.windows.net/value_stream_monitoring/databricks_storage_costs_archive_staging"

spark.conf.set("spark.sql.shuffle.partitions", "10")

try:
    raw = spark.read.format("csv").option("header", "true").load(source_path)
except Exception as e:
    dbutils.notebook.exit(f"WARNING: Read failed: {e}")

raw = raw.toDF(*[c.strip().lstrip("﻿") for c in raw.columns])

df = (
    raw.select(
        F.coalesce(
            F.expr(f"try_to_timestamp(`{date_col}`, 'yyyy-MM-dd')"),
            F.expr(f"try_to_timestamp(`{date_col}`, 'yyyyMMdd')"),
            F.expr(f"try_to_timestamp(`{date_col}`, 'M/d/yyyy')"),
        ).cast("date").alias("UsageDate"),
        F.col(meter_col).alias("Meter"),
        F.col(cost_col).cast("double").alias("Cost"),
    )
    .where(F.col("UsageDate").isNotNull() & F.col("Meter").isNotNull())
    .groupBy("UsageDate", "Meter")
    .agg(F.sum("Cost").alias("Cost"))
)

df.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .option("path", staging_path) \
    .saveAsTable(staging_name)

if not spark.catalog.tableExists(table_name):
    spark.sql(f"""
        CREATE TABLE {table_name}
        USING DELTA
        LOCATION '{delta_path}'
        AS SELECT * FROM {staging_name}
    """)
else:
    spark.sql(f"""
        MERGE INTO {table_name} AS tgt
        USING {staging_name} AS src
        ON tgt.UsageDate = src.UsageDate
            AND tgt.Meter = src.Meter
        WHEN MATCHED THEN UPDATE SET tgt.Cost = src.Cost
        WHEN NOT MATCHED THEN INSERT *
    """)

spark.sql(f"DROP TABLE IF EXISTS {staging_name}")