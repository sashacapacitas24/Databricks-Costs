import pandas as pd
from azure.identity import InteractiveBrowserCredential
from azure.mgmt.costmanagement  import CostManagementClient
from azure.mgmt.costmanagement.models import (QueryDefinition, QueryTimePeriod, QueryDataset, QueryAggregation, QueryGrouping, TimeframeType)
from datetime import datetime, timedelta

subscription_id = "3e382e88-0bab-40ca-a6b4-3c256a238fa7"
credential = InteractiveBrowserCredential()
client=CostManagementClient(credential)
scope=f"/subscriptions/{subscription_id}"

start_date = datetime(2026,7,13)
end_date = datetime(2026,7,14)

query = QueryDefinition(
    type="AmortizedCost",
    timeframe=TimeframeType.CUSTOM,
    time_period=QueryTimePeriod(
        from_property=start_date,
        to=end_date
    ),
    dataset=QueryDataset(
        granularity="Daily", 
        aggregation={
            "totalCost": QueryAggregation(
                name="Cost", 
                function="Sum"
            )
        },
        grouping=[
            QueryGrouping(
                type="Dimension", 
                name="Meter"
            ),
            QueryGrouping(
                type="Dimension", 
                name="ServiceName"
            )
        ], 
        filter={
            "dimensions":{
                "name": "ServiceName",
                "operator": "In",
                "values": ["Azure Databricks"]
            }
        }
    )
)
result = client.query.usage(scope, query)
rows=[]
columns = [col.name for col in result.columns]
for row in result.rows:
    rows.append(dict(zip(columns, row)))
    
dfDatabricksCosts = pd.DataFrame(rows)

print(dfDatabricksCosts)

