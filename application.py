import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import plotly.figure_factory as ff
import numpy as np
import base64


# Launch the application:

app = dash.Dash()
server = app.server
app.config.suppress_callback_exceptions=True


# Data cleaning: Years
years=pd.read_csv('https://query.data.world/s/yzwhxgzdkug4f7gbu3tasyjelyww7g')
years=years.drop('county', axis=1)
years=years.T.reset_index()
years.columns='year','rate'
years['rate']=round(years['rate'],1)

# Data cleaning: Counties
df=pd.read_csv('https://data.world/naimmerchant/virgiasealevelv1/workspace/file?filename=va-climate-test.csv')
df=df[pd.to_numeric(df['rate_2016'], errors='coerce').notnull()]
df['rate_2016']=round(df['rate_2016'].astype(float),1)
df['locality']=df['locality'].str.split(' County').str[0]
df['locality']=df['locality'].str.split(' City').str[0]
df=df[df['locality']!='TOTAL']
df=df.sort_values('locality', ascending=True).reset_index(drop=True)

# Data cleaning: FIPS codes
FIPS=pd.read_csv('https://query.data.world/s/b4eko5jc6x7fuqdzq2nzrrxitruxc2')
FIPS.columns=['FIPS','name']
FIPS=FIPS.sort_values('name', ascending=True).reset_index(drop=True)
FIPS['name']=FIPS['name'].str.split(' City').str[0]
FIPS['name']=FIPS['name'].str.split(' County').str[0]

# Join FIPS and County Data
opi=df.join(FIPS)
len(opi[opi['locality']!=opi['name']])
opi=opi.drop(['name'], axis=1)

# Set up the map values
colorscale = ["#f7fbff","#ebf3fb","#deebf7","#d2e3f3","#c6dbef","#b3d2e9","#9ecae1",
              "#85bcdb","#6baed6","#57a0ce","#4292c6","#3082be","#2171b5","#1361a9",
              "#08519c","#0b4083","#08306b"]
endpts = list(np.linspace(1, 50, len(colorscale) - 1))
fips = opi['FIPS'].tolist()
values = opi['rate_2016'].tolist()

# Designate the IMAGES
deloitte = base64.b64encode(open('Deloitte_Logo.png', 'rb').read())
dataworld = base64.b64encode(open('owl.png', 'rb').read())

# Create a choropleth map of Counties
fig = ff.create_choropleth(
    fips=fips, values=values,scope=['Virginia'],
    show_state_data=True,
    binning_endpoints=endpts,
    colorscale=colorscale,
    show_hover=True, centroid_marker={'opacity': 0},
    asp=2.9, title='Fatal Opioid Overdose Rate by County: 2016',
    legend_title='Rate per 100K'
)

# App Layout
app.layout = html.Div([

    html.H1(children='Rise in Opioid Deaths: A Health Crisis in Virginia'),

    dcc.Graph(
                id='my-graph',
                figure=fig
            ),
    dcc.Graph( # Create a Bar chart of years
        id='years',
        figure={
            'data': [
                go.Bar(
                    x = years['year'],
                    y = years['rate']
                )
            ],
            'layout': go.Layout(
                title='State-wide Rate of Fatal Opioid Overdoses',
                xaxis = dict(title = 'Year'), # x-axis label
                yaxis = dict(title = 'Rate per 100,000 People'),
                hovermode='closest'
            )
        }
    ),
        html.Div([
            html.Img(src='data:image/png;base64,{}'.format(deloitte.decode()), style={'width': '300px'}),
            html.Img(src='data:image/png;base64,{}'.format(dataworld.decode()), style={'width': '300px'}),
        ], className="Row"),
        html.A('https://data.world/alasseter/va-opioid-test', href='https://data.world/alasseter/va-opioid-test', style={'margin':40})
])



app.css.append_css({'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'})

if __name__ == '__main__':
    app.run_server()
