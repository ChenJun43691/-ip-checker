from ip_query import batch_query
import asyncio

ip_list = ["8.8.8.8", "1.1.1.1"]
results = asyncio.run(batch_query(ip_list))
print(results)