import pandas as pd

#whatever source you are using to get the cost data, location can change 
dfDatabricksCosts = pd.read_csv(rf"\\acs09w497.corp.alldata.net\UserFolders\a835877\Documents\Peak 2026\Databricks\csv\Adhoc Databricks Costs.csv")

#find the total for the SKU you are looking at, seperate file containing query
PREMIUM_ALL_PURPOSE_SERVERLESS_COMPUTE_US_EAST_2_total_usage = 3186.328956853275465521

#extracted data from databricks, see seperate query to see what to run in databricks
dfTotalUsage = pd.read_csv(r"\\acs09w497.corp.alldata.net\UserFolders\a835877\Documents\Peak 2026\Databricks\Notebook Level\usage_by_notebook_daily.csv")


PREMIUM_ALL_PURPOSE_SERVERLESS_COMPUTE_US_EAST_2_total_cost = dfDatabricksCosts.loc[dfDatabricksCosts["Meter"] == "Premium Interactive Serverless Compute DBU", "Cost"].sum()
top_100_usage = dfTotalUsage['total_usage'].sum()

dfTotalUsage['Cost'] = (((dfTotalUsage['total_usage']/PREMIUM_ALL_PURPOSE_SERVERLESS_COMPUTE_US_EAST_2_total_usage)*PREMIUM_ALL_PURPOSE_SERVERLESS_COMPUTE_US_EAST_2_total_cost))
dfTotalUsage['Notebook Annual Cost'] = (((dfTotalUsage['total_usage']/PREMIUM_ALL_PURPOSE_SERVERLESS_COMPUTE_US_EAST_2_total_usage)*PREMIUM_ALL_PURPOSE_SERVERLESS_COMPUTE_US_EAST_2_total_cost))*365


print(dfTotalUsage)

#this is in case your query extract had a limit filter
print(rf"% covered is {(top_100_usage/PREMIUM_ALL_PURPOSE_SERVERLESS_COMPUTE_US_EAST_2_total_usage)*100}")

