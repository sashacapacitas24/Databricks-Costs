import pandas as pd
from azure.identity import InteractiveBrowserCredential
from azure.mgmt.costmanagement  import CostManagementClient
from azure.mgmt.costmanagement.models import (QueryDefinition, QueryTimePeriod, QueryDataset, QueryAggregation, QueryGrouping, TimeframeType)
from datetime import datetime, timedelta

dfDatabricksCosts = pd.read_csv(rf"\\acs09w497.corp.alldata.net\UserFolders\a835877\Documents\Peak 2026\Databricks\Monthly Databricks Costs.csv")
dfDatabricksCosts = dfDatabricksCosts.drop(columns=['CostUSD', 'Currency'])
dfDatabricksCosts['UsageDate'] = dfDatabricksCosts['UsageDate'].astype(str)
print(dfDatabricksCosts)
dfDatabricksUsage = pd.read_csv(rf"\\acs09w497.corp.alldata.net\UserFolders\a835877\Documents\Peak 2026\Databricks\total_monthly_dbu.csv")
dfDatabricksUsage['Date'] = pd.to_datetime(dfDatabricksUsage['year'].astype(str) + '-' + dfDatabricksUsage['month'].astype(str) + '-01')
dfDatabricksUsage = dfDatabricksUsage.drop(columns=['year', 'month'])
dfDatabricksUsage['Date'] = dfDatabricksUsage['Date'].astype(str)
dfDatabricksUsage['total_usage'] = pd.to_numeric(dfDatabricksUsage['total_usage'])


dfDatabricksCosts = dfDatabricksCosts.merge(dfDatabricksUsage, left_on='UsageDate', right_on='Date', how='inner')
dfDatabricksCosts=dfDatabricksCosts.drop(columns=['Date'])
pd.set_option('display.float_format', '{:.2f}'.format)
dfDatabricksCosts['Cost per DBU'] = dfDatabricksCosts['Cost']/dfDatabricksCosts['total_usage']
print(dfDatabricksCosts)

dfDatabricksCosts.to_csv(
    r"\\acs09w497.corp.alldata.net\UserFolders\a835877\Documents\Peak 2026\Databricks\price_per_dbu.csv", index=False
)

dfDatabricksCosts.to_json(
    r"\\acs09w497.corp.alldata.net\UserFolders\a835877\Documents\Peak 2026\Databricks\price_per_dbu.json", index=False
)