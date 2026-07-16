import pandas as pd

Workspace = "dbx-ads-eus2-edh-prd-001"
Job_id = "264927174368064"

#the databricks cost extract from azure
dfDatabricksCosts = pd.read_csv(rf"\\acs09w497.corp.alldata.net\UserFolders\a835877\Documents\Peak 2026\Databricks\Workspace Level\Daily Workspace Costs - {Workspace}.csv")

#Databricks usage - currently filtered to the job_id specified at the top but this can be removed- seperate query to follow
dfDatabricksBilling= pd.read_csv(rf"\\acs09w497.corp.alldata.net\UserFolders\a835877\Documents\Peak 2026\Databricks\Job Level\{Job_id} usage data.csv")

#total databricks usage - seperate query to follow
dfTotalUsage = pd.read_csv(rf"\\acs09w497.corp.alldata.net\UserFolders\a835877\Documents\Peak 2026\Databricks\Workspace Level\PREMIUM_JOBS_SERVERLESS_COMPUTE_US_EAST_2 - {Workspace}.csv")

meter_mapping = {
    'premium all-purpose photon dbu': 'PREMIUM_ALL_PURPOSE_COMPUTE_(PHOTON)',
    'premium all-purpose compute dbu': 'PREMIUM_ALL_PURPOSE_COMPUTE',
    'premium anthropic serverless inference dbu': 'PREMIUM_ANTHROPIC_MODEL_SERVING',
    'premium automated serverless compute dbu': 'PREMIUM_JOBS_SERVERLESS_COMPUTE_US_EAST_2',
    'premium core compute delta live tables dbu': 'PREMIUM_DLT_CORE_COMPUTE',
    'premium interactive serverless compute dbu': 'PREMIUM_ALL_PURPOSE_SERVERLESS_COMPUTE_US_EAST_2',
    'premium jobs compute dbu': 'PREMIUM_JOBS_COMPUTE',
    'premium jobs compute photon dbu': 'PREMIUM_JOBS_COMPUTE_(PHOTON)',
    'premium model training dbu': 'PREMIUM_MODEL_TRAINING_US_EAST_2',
    'premium sql analytics dbu': 'PREMIUM_SQL_COMPUTE',
    'premium serverless realtime inferencing dbu': 'PREMIUM_SERVERLESS_REAL_TIME_INFERENCE_US_EAST_2',
    'premium serverless sql dbu': 'PREMIUM_SERVERLESS_SQL_COMPUTE_US_EAST_2'
}

def transform_azure_billing(df):
    df['Meter'] = df['Meter'].str.lower().str.strip()
    df['sku_mapped'] = df['Meter'].map(meter_mapping)
    df['UsageDate'] = df['UsageDate'].astype('float64')
    return df

def transform_databricks_billing(df):
    df['sku_name'] = df['sku_name'].str.upper()
    df['usage_date'] = df['usage_date'].str.replace('-', '')
    df['usage_date'] = df['usage_date'].astype('float64')
    return df

dfDatabricksCosts = transform_azure_billing(dfDatabricksCosts)
dfDatabricksBilling = transform_databricks_billing(dfDatabricksBilling)
dfTotalUsage = transform_databricks_billing(dfTotalUsage)

dfDatabricksCosts=dfDatabricksCosts[dfDatabricksCosts['sku_mapped'].isin(dfTotalUsage['sku_name'])]
dfTotalUsage=dfTotalUsage.merge(dfDatabricksCosts, left_on=['sku_name', 'usage_date'], right_on=['sku_mapped', 'UsageDate'] )


df_merge = dfDatabricksBilling.merge(dfTotalUsage, on=['usage_date'], how='left')
df_merge=df_merge.drop(columns=['sku_name_y', 'UsageDate', 'Meter', 'ServiceName', 'ResourceId', 'Currency', 'sku_mapped'])
df_merge=df_merge.rename(columns={
    'sku_name_x': 'SKU',
    'usage_date': 'Date', 
    'total_usage_x': 'Job Daily Usage', 
    'total_usage_y': 'Meter Daily Usage', 
    'Cost': 'Daily Meter Cost'
})
df_merge['Job Daily Cost'] = (df_merge['Job Daily Usage']/df_merge['Meter Daily Usage'])*df_merge['Daily Meter Cost']

