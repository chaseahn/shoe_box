import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import sqlite3

conn = sqlite3.connect("shoebox.db")
df = pd.read_sql_query("SELECT * FROM sneakers WHERE total_sales NOT LIKE '%--%' and avg_sale_price NOT LIKE '%--%' and total_sales > 500 and avg_sale_price > 100", conn)

conn.close()

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.Graph(
        id='sales-v-premium',
        figure={
            'data': [
                go.Scatter(
                    x=df[df['brand'] == i]['avg_sale_price'],
                    y=df[df['brand'] == i]['total_sales'],
                    text=df[df['brand'] == i]['name'],
                    mode='markers',
                    opacity=0.7,
                    marker={
                        'size': 15,
                        'line': {'width': 0.5, 'color': 'white'}
                    },
                    name=i
                ) for i in df.brand.unique()
            ],
            'layout': go.Layout(
                xaxis={'type': 'log', 'title': 'Sneaker Value'},
                yaxis={'title': 'Total Sales'},
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            )
        }
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)