import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px

if __name__ == '__main__':
    data = pd.read_csv('data.csv')
    products_info = pd.read_csv('data_shops.csv')
    x = products_info.groupby('day').sum()
    data = pd.merge(data, x.drop(labels='shop_id', axis=1), on='day')
    data = data.astype(int)

    data = data.sort_values(by='day')
    data['step'] = 0
    sum_df = pd.DataFrame(columns=data.columns)

    for i in range(len(data)):
        data['step'] = i
        sum_df = pd.concat([sum_df, data[:i + 1]])

    fig = px.line(sum_df, x='day', animation_frame='step', y=sum_df.drop(['day', 'step'], 1).columns)
    fig.show()
