import random

import pandas as pd
import numpy as np

number_days = 10
number_shops = 28
data = []


column_names = ['profit', 'discount_lose', 'summary_sales', 'completed_orders', 'day']
for i in range(number_days):
    now = {}
    for col in column_names:
        now[col] = random.randint(1, 5)
    now['day'] = i
    data.append(now)

data = pd.DataFrame(data)
data.to_csv('data.csv', index=False)

product_names = ["egg", "fish", 'meat', 'apple', 'pear', 'milk', 'water', 'bread', 'cake',
                     'napkins', 'soap', 'shampoo', 'coal', 'beer', 'porrige', 'apple juice',
                     'cherry juice', 'crakers', 'domestos', 'tomato']
data = []
column_names = product_names + ['shop_id', 'day']
for i in range(number_days):
    # print(chosen_shops.sum())
    # print(chosen_shops[0])
    shops = [{'shop_id': j, 'day': i} for j in range(number_shops)]

    for name in product_names:
        chosen_shops = np.random.choice([True, False], number_shops, p=[0.2, 0.8])
        for shop_id in range(number_shops):
            if chosen_shops[shop_id] == False:
                continue

            shops[shop_id][name] = random.randint(0, 4)

    data += shops

data = pd.DataFrame(data).fillna(0)
data.to_csv('data_shops.csv', index=False)
