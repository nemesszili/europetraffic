import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

import pandas as pd
import numpy as np
import json
import pycountry

from util.data import *

external_css = ['https://stackpath.bootstrapcdn.com/bootstrap/4.2.1/css/bootstrap.min.css']

external_js = [
    'https://code.jquery.com/jquery-3.3.1.slim.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.6/umd/popper.min.js',
    'https://stackpath.bootstrapcdn.com/bootstrap/4.2.1/js/bootstrap.min.js'
]

app = dash.Dash(
    __name__,
    external_scripts=external_js,
    external_stylesheets=external_css,
)
app.title = 'Traffic mortality'

layout = dict(
    width = 650,
    height = 650,
    geo = dict(
        resolution = '50',
        scope = 'europe',
        lonaxis = dict(
            range = [-20, 30],
            dtick = 0
        ),
        lataxis = dict(
            range = [35, 75],
            dtick = 0
        ),
        showframe = True,
        showcoastlines = True,
        projection = dict(
            type = 'Mercator'
        ),
    ),
    clickmode='event+select'
)

data = dict(
    type = 'choropleth',
    locations = [],
    z = [],
    text = [],
    colorscale = [[0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],\
        [0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"]],
    autocolorscale = False,
    reversescale = True,
    marker = dict(
        line = dict (
            color = 'rgb(180,180,180)',
            width = 0.5
        )
    ),
    colorbar = dict(
        autotick = True
    ),
)

categoryDropdownOptions = {
    'by_road_user': [],
    'by_vehicle': [],
    'by_age': []
}

for cat in list(by_road_user['category'].unique()):
    categoryDropdownOptions['by_road_user'].append({'label': cat, 'value': cat})
for cat in list(by_vehicle['category'].unique()):
    categoryDropdownOptions['by_vehicle'].append({'label': cat, 'value': cat})
for cat in list(by_age['category'].unique()):
    categoryDropdownOptions['by_age'].append({'label': cat, 'value': cat})

app.layout = html.Div(children=[
    html.H1('Traffic mortality statistics of Europe (2001-2016)', className='text-center', id='header'),

    html.Div(className='container', children=[
        html.Div(className='row', children=[
        html.Div(className='col-sm-7', children=[
            html.Div(
                style={'marginLeft': '50px', 'marginBottom': '20px'},
                children=[
                html.Div('Select year: ', style={'width': '18rem'}),
                dcc.Slider(
                    id='year-slider',
                    min=2001,
                    max=2016,
                    value=2001,
                    marks={str(year): str(year) for year in range(2001, 2017)}
                )
            ]),
            dcc.Graph(
                id='map',
                hoverData={'points': [
                    {
                        "curveNumber": 0,
                        "pointNumber": 4,
                        "pointIndex": 4,
                        "location": "DEU",
                        "text": "Germany"
                    }
                ]},
                figure=dict(data=[data], layout=layout)
            )
        ]),

        html.Div(className='col-sm-1', children=[]),
        html.Div(className='col-sm-4', children=[
            html.Div(className='container', children=[
                html.Div(children=[
                    html.Div('Mortality by:'),
                    dcc.Dropdown(
                        id='dataset',
                        options=[
                            {'label': 'Road user', 'value': 'by_road_user'},
                            {'label': 'Vehicle', 'value': 'by_vehicle'},
                            {'label': 'Age', 'value': 'by_age'},
                        ],
                        value='by_road_user',
                    ),
                ]),
                html.Div(children=[
                    html.Div('Select category:'),
                    dcc.Dropdown(
                        id='category',
                        options=categoryDropdownOptions['by_road_user'],
                        value=categoryDropdownOptions['by_road_user'][0]["value"]
                    ),
                ]),
                html.Div(children=[
                    html.Div('Unit:'),
                    dcc.Dropdown(
                        id='unit',
                        options=[
                            {'label': 'Number', 'value': 'num'},
                            {'label': 'Per million inhabitants', 'value': 'million'}
                        ],
                        value='num'
                    )
                ]),
                html.Div(className='row', children=[html.P(children=[])]),
                html.Div(className='container', children=[
                    html.Div(className='row', children=[
                        html.Div(className='col-sm-12', children=[
                            html.Div(
                                className='card',
                                children=[
                                    html.Div('Country information', className='card-header'),
                                    html.Div(
                                        className='card-body text-left', 
                                        children=[
                                            html.H5(id='country', className='card-title'),
                                            html.P(
                                                className='card-text',
                                                children=[
                                                    html.P(id='population'),
                                                    html.P(id='roads', style={'white-space': 'pre-line'}),
                                                    html.P(id='vehicleStock', style={'white-space': 'pre-line'})
                                                ])
                                    ])
                            ]),
                        ]),
                    ]),
                ]),
            ]),
        ]),		
    ]),
    html.Div(className='row', children=[
        html.Div(className='col-sm-12', children=[
            dcc.Graph(id='hist-comparison')
        ]),
    ]),
    ]),
    
    html.Div(id='output-container')
])

@app.callback(
    dash.dependencies.Output(component_id='country', component_property='children'),
    [dash.dependencies.Input(component_id='map', component_property='hoverData')],
    [dash.dependencies.State(component_id='year-slider', component_property='value')]
)
def hover_country_name(hoverData, year):
    ret = ""
    if hoverData:
        hoverData = hoverData['points'][0]
        ret = hoverData['text']

    return ret

@app.callback(
    dash.dependencies.Output(component_id='population', component_property='children'),
    [dash.dependencies.Input(component_id='map', component_property='hoverData')],
    [dash.dependencies.State(component_id='year-slider', component_property='value')]
)
def hover_population(hoverData, year):
    ret = ""
    if hoverData:
        hoverData = hoverData['points'][0]
        country = hoverData['location']
        val = float(population[(population['code'] == country) & (population['time'] == year)]['value'].values[0]) / 1e6
        ret = "Population: %.2f million" % (val)

    return ret

@app.callback(
    dash.dependencies.Output(component_id='roads',component_property='children'),
    [dash.dependencies.Input(component_id='map',component_property='hoverData')],
    [dash.dependencies.State(component_id='year-slider',component_property='value')]
)
def hover_roads(hoverData, year):
    ret = ""
    if hoverData:
        hoverData = hoverData['points'][0]
        country = hoverData['location']
        roads = road_motorways[(road_motorways['code'] == country) & (road_motorways['time'] == year)]
        ret = ""
        for index, row in roads.iterrows():
            val = int(row['value'])
            if val > 0:
                ret += row['tra_infr'] + ": " + str(val) + " km\n"
            else:
                ret += row['tra_infr'] + ": N/A\n"

    return ret

@app.callback(
    dash.dependencies.Output(component_id='vehicleStock',component_property='children'),
    [dash.dependencies.Input(component_id='map',component_property='hoverData')],
    [dash.dependencies.State(component_id='year-slider',component_property='value')]
)
def hover_vehicles(hoverData, year):
    ret = ""
    if hoverData:
        hoverData = hoverData['points'][0]
        country = hoverData['location']
        val = int(vehicle_stock[(vehicle_stock['code'] == country) & (vehicle_stock['time'] == year)]['value'].values[0])
        if val > 0:
            ret = "Vehicles per capita: " + str(val)
        else:
            ret = "Vehicles per capita: N/A"

    return ret

@app.callback(
    dash.dependencies.Output(component_id='category',component_property='options'),
    [dash.dependencies.Input(component_id='dataset', component_property='value')]
)
def update_categories_options(value):
    return categoryDropdownOptions[value]

@app.callback(
    dash.dependencies.Output(component_id='category', component_property='value'),
    [dash.dependencies.Input(component_id='category', component_property='options')]
)
def update_categories_value(options):
    return options[0]['value']

val_to_label = {
    'by_road_user': 'Road user',
    'by_vehicle': 'Vehicle',
    'by_age': 'Age'
}

@app.callback(
    dash.dependencies.Output(component_id='map', component_property='figure'),
    [
        dash.dependencies.Input(component_id='category', component_property='value'),
         dash.dependencies.Input(component_id='year-slider', component_property='value'),
         dash.dependencies.Input(component_id='dataset', component_property='value'),
         dash.dependencies.Input(component_id='unit', component_property='value')
    ]
)
def update_map(category, year, dataset, unit):
    if dataset == 'by_road_user':
        data_to_pres = by_road_user[(by_road_user['category'] == category) & (by_road_user['time'] == year)]
    elif dataset == 'by_vehicle':
        data_to_pres = by_vehicle[(by_vehicle['category'] == category) & (by_vehicle['time'] == year)]
    elif dataset == 'by_age':
        data_to_pres = by_age[(by_age['category'] == category) & (by_age['time'] == year)]
    
    val = data_to_pres['value']
    if unit == 'million':
        country = data_to_pres['code']
        pop = population[(population['code'].isin(country)) & (population['time'] == year)]
        pop = pop.drop_duplicates(subset=['code'], keep='first')
        pop = pop['value']
        pop /= 1e6
        val = data_to_pres['value'].div(pop.values)
    
    return {
        "data": [
            dict(
                type = 'choropleth',
                locations = data_to_pres['code'],
                z = val,
                text = data_to_pres['geo'],
                colorscale = [[0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],\
                    [0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"]],
                autocolorscale = False,
                reversescale = True,
                marker = dict(
                    line = dict (
                        color = 'rgb(180,180,180)',
                        width = 0.5
                    )
                ),
                colorbar = dict(
                    autotick = True,
                    title = val_to_label[dataset]
                ),
            )],
        "layout": layout
    }

@app.callback(
    dash.dependencies.Output(component_id='hist-comparison', component_property='figure'),
    [
        dash.dependencies.Input(component_id='map', component_property='selectedData'),
        dash.dependencies.Input(component_id='dataset', component_property='value'),
        dash.dependencies.Input(component_id='category', component_property='value'),
        dash.dependencies.Input(component_id='unit', component_property='value')
    ]
)
def update_historical(selectedData, dataset, category, unit):
    if dataset == 'by_road_user':
        data_to_pres = by_road_user[by_road_user['category'] == category]
    elif dataset == 'by_vehicle':
        data_to_pres = by_vehicle[by_vehicle['category'] == category]
    elif dataset == 'by_age':
        data_to_pres = by_age[by_age['category'] == category]

    title = 'Mortality by %s (%s)' % (val_to_label[dataset], category)
    if unit == 'million':
        title += ' per million inhabitants'

    countries = []
    if selectedData:
        for sel in selectedData['points']:
            countries.append(sel['location'])

    traces = []
    for country in countries:
        y_series = data_to_pres[(data_to_pres['code'] == country) & \
                                (data_to_pres['time'] < 2017)]['value']
        if unit == 'million':
            pop = population[(population['code'] == country) & \
                             (population['time'] < 2017)]
            if len(pop) > 30:
                pop = pop.iloc[::2, :]
            pop = pop['value']
            pop /= 1e6
            y_series = y_series.div(pop.values)
        else:
            y_series = y_series.values
        traces.append(go.Scatter(
            x = np.arange(2001, 2017),
            y = y_series,
            mode='lines',
            name=country,
            connectgaps=True
        ))

    return {
        'data': traces,
        'layout': go.Layout(
            title=title,
            margin={'l': 40, 'b': 30, 't': 50, 'r': 40},
            height=450,
            hovermode='closest',
            xaxis=dict(
                tickmode='array'
            )
        )
    }

if __name__ == '__main__':
    app.run_server(debug=True)
