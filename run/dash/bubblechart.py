import sqlite3
import plotly
import plotly.plotly as py
import plotly.graph_objs as go

import pandas as pd

plotly.tools.set_credentials_file(username='ChaseAhn', api_key='bP3d9mByY0LnICLFi5Bh')
plotly.tools.set_config_file(plotly_domain='https://plotly.0.0.0.0:5000',
                             plotly_streaming_domain='https://stream-plotly.0.0.0.0:5000',
                             world_readable=True,
                             sharing='public')

# Get Data: this ex will only use part of it (i.e. rows 750-1500)
conn = sqlite3.connect("shoebox.db")
df = pd.read_sql_query("SELECT * FROM sneakers WHERE total_sales NOT LIKE '%--%' and avg_sale_price NOT LIKE '%--%' and total_sales > 500 and avg_sale_price > 100", conn)
conn.close()

trace1 = go.Scatter3d(
    x=df['brand'],
    y=df['type'],
    z=df['total_sales'],
    text=df['name'],
    mode='markers',
    marker=dict(
        sizemode='diameter',
        sizeref=750,
        size=df['avg_sale_price'],
        color = df['premium'],
        colorscale = 'Viridis',
        colorbar = dict(title = 'Life<br>Expectancy'),
        line=dict(color='rgb(140, 140, 170)')
    )
)

data=[trace1]

layout=go.Layout(height=800, width=800, title='Examining Population and Life Expectancy Over Time')

fig=go.Figure(data=data, layout=layout)
py.iplot(fig, filename='3DBubble')