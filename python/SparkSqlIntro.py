from pyspark import SparkContext
from pyspark.sql import SQLContext
from pyspark.sql import Row
sqlContext = SQLContext(sc)
dividends = sc.textFile('/home/anant/projects/spark-examples/data/NYSE_dividends_A.csv')
daily_prices = sc.textFile('/home/anant/projects/spark-examples/data/NYSE_daily_prices_A.csv')
dividends_parsed = dividends.filter(lambda r: not r.startswith('exchange')).map(lambda r: r.split(',')).map(
  lambda row: Row(**{'exchange': row[0], 'stock_symbol': row[1], 'date': row[2], 'dividends': float(row[3])}))


dividends_schema = sqlContext.inferSchema(dividends_parsed)
dividends_schema.printSchema()
dividends_schema.registerAsTable('dividends')

result = sqlContext.sql('SELECT * from dividend').collect()
for row in result:
    print row

columns = daily_prices.take(1)[0].split(',')
print columns

daily_prices_parsed = daily_prices.filter(lambda r: not r.startswith('exchange')).map(lambda r: r.split(',')).map(
lambda row: Row(**{columns[0]: row[0], columns[1]: row[1], columns[2]: row[2],
columns[3]: float(row[3]), columns[4]: float(row[4]), columns[5]: float(row[5]),
columns[6]: float(row[6]), columns[7]: float(row[7]), columns[8]: float(row[8])}))
daily_prices_schema = sqlContext.inferSchema(daily_prices_parsed)
daily_prices_schema.printSchema()

daily_prices_schema.registerAsTable('daily_prices')
result = sqlContext.sql('SELECT * FROM daily_prices LIMIT 10').collect()
for row in result:
    print row

join = sqlContext.sql('''SELECT div.exchange, div.stock_symbol, div.date, div.dividends, prices.stock_price_adj_close,
prices.stock_price_close  FROM dividends div INNER JOIN daily_prices prices
ON(div.stock_symbol=prices.stock_symbol AND div.date=prices.date) LIMIT 10''').collect()
for row in join:
    print row

join_group = sqlContext.sql('''SELECT div.stock_symbol, max(prices.stock_price_close) as max_close FROM dividends div 
INNER JOIN daily_prices prices ON(div.stock_symbol=prices.stock_symbol AND div.date=prices.date) 
GROUP BY div.stock_symbol LIMIT 10''').collect()
for row in join_group:
    print join_group

join_group_agg = sqlContext.sql('''SELECT div.stock_symbol, max(prices.stock_price_close) maximum,
min(prices.stock_price_close) minimum, avg(prices.stock_price_close) average FROM dividends div 
INNER JOIN daily_prices prices ON(div.stock_symbol=prices.stock_symbol AND div.date=prices.date) 
GROUP BY div.stock_symbol LIMIT 10''').collect()
for row in join_group_agg:
    print row



