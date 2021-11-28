import time
import traceback

import pandas as pd
from datetime import timedelta, datetime
import PySimpleGUI as sg
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
from threading import Thread


class Drawer(Thread):
    def __init__(self, data, time_step):
        Thread.__init__(self)
        self.data = data
        self.running = False
        self.time_step = timedelta(seconds=time_step)
        self.ind = 0
        self.fig = make_subplots(2, 3)

    def update_view(self):
        if self.ind == len(data):
            return
        print('updating fig')

        self.ind += 1
        self.fig.data = []
        self.fig.add_trace(
            go.Line(x=list(range(self.ind)), y=data[:self.ind]['profit'], name='summary_sales'),
            row=1, col=1
        )

        self.fig.add_trace(
            go.Line(x=list(range(self.ind)), y=data[:self.ind]['discount_lose']),
            row=1, col=2
        )

        self.fig.add_trace(
            go.Line(x=list(range(self.ind)), y=data[:self.ind]['summary_sales']),
            row=1, col=3
        )

        self.fig.update_layout(height=600, width=800, title_text="Side By Side Subplots")
        print(self.fig.data)
        self.fig.show()
        # pio.write_html(self.fig, file='index.html', auto_open=False, auto_play=True)

    def run(self):
        last_draw = datetime.now() - self.time_step
        print('running')
        while True:
            if not self.running:
                continue
            if last_draw + self.time_step <= datetime.now():
                last_draw = datetime.now()
                self.update_view()
            time.sleep(0.01)


class App:
    text_size = (25, 1)
    input_size = (25, 1)
    button_size = (15, 1)
    layout = [
        [sg.Text('Number of days (N)', size=text_size),
         sg.InputText(size=input_size, key="days", default_text='50')],
        [sg.Text('Number of products (K)', size=text_size),
         sg.InputText(size=input_size, key="products", default_text='7')],
        [sg.Text('Number of shops (M)', size=text_size),
         sg.InputText(size=input_size, key="shops", default_text='10')],
        [sg.Button('Start', size=button_size, key='start')]
    ]
    centre_layout = [[sg.Column(layout, element_justification='center')]]

    def __init__(self, data):
        # sg.set_options(font=("Any", 16), button_color=('blue', None))
        self.window = sg.Window(title='Storage simulation', layout=self.centre_layout)
        self.data = data
        # self.fig = make_subplots(2, 3)

    def run(self):
        while True:
            event, values = self.window.read()
            print(event, values)
            if event in (None, 'Exit', 'Cancel', sg.WIN_CLOSED):
                break

            if event == 'start':
                fig = px.line(self.data, x='day', animation_frame='step', y=self.data.drop(['day', 'step'], 1).columns)
                fig.show()

            time.sleep(0.01)


if __name__ == '__main__':
    data = pd.read_csv('data.csv')
    products_info = pd.read_csv('data_shops.csv')
    x = products_info.groupby('day').sum()
    data = pd.merge(data, x.drop(labels='shop_id', axis=1), on='day')
    data = data.astype(int)
    # print(data.columns)
    # exit(0)

    data = data.sort_values(by='day')
    data['step'] = 0
    sum_df = pd.DataFrame(columns=data.columns)

    for i in range(len(data)):
        data['step'] = i
        sum_df = pd.concat([sum_df, data[:i + 1]])

    app = App(sum_df)
    try:
        app.run()
    except:
        print(traceback.format_exc())
