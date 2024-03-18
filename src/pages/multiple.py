from dash import html, dcc, Output, Input, register_page, callback, dash_table, State
import dash.dash_table.FormatTemplate as FormatTemplate
from datetime import datetime, timedelta
import dash_bootstrap_components as dbc
import requests
import json
import pathlib
import pandas as pd
from navbar import navbar


register_page(__name__, path='/predict/multiple-prediction')

BASE_DIR = pathlib.Path(__file__).resolve().parent

data = pd.read_csv(BASE_DIR.parent.parent / 'Data/needed_food_data.csv')
Maize_data = pd.read_csv(BASE_DIR.parent.parent / 'Data/maize.csv')
Beans_data = pd.read_csv(BASE_DIR.parent.parent / 'Data/beans.csv')
Rice_data = pd.read_csv(BASE_DIR.parent.parent / 'Data/rice.csv')


layout = html.Div([
    dcc.Location(id='url'),
    navbar,
    html.Div(
        style={'padding': '5%', 'paddingTop': '100px',
               'display': 'grid', 'gap': '25px'},

        children=[
            dcc.Dropdown(
                id='select-market',
                options=[{'label': market, 'value': market}
                         for market in data['market'].unique()],
                value=[market for market in data['market'].unique()],
                multi=True
            ),

            dcc.Dropdown(
                id='select-commodity',
                options=[{'label': commodity, 'value': commodity}
                         for commodity in data['commodity'].unique()],
                value=[commodity for commodity in data['commodity'].unique()],
                multi=True
            ),

            html.Div(
                style={'display': 'flex', 'gap': '3rem',
                       'justifyContent': 'center'},
                children=[
                    dbc.Input(type="number", min=1, max=6, step=1, placeholder="Enter month length (up to 6 months)",
                              id='month-length', persistence=True, style={'paddingRight': '20px'}),
                    dbc.Button('Predict', id='multiple-predict',
                               color='success', n_clicks=0, style={'width': '180px'}),
                    dbc.Button(
                        [html.I(className="bi bi-download"), "Download CSV"],
                        style={'width': '180px'}
                    )
                ]
            ),

            dbc.Card([
                dbc.CardBody([
                    dash_table.DataTable(
                        id='table',
                        page_size=15,
                        style_header={
                            'fontWeight': 'bold',
                            'textAlign': 'center',
                            'textTransform': 'capitalize',
                            'backgroundColor': 'rgba(211, 211, 211, 0.7)',
                            'textShadow': '2px 2px 4px rgba(0,0,0,0.4)',
                            'fontSize': '14px'
                        },
                        style_data={
                            'textAlign': 'center',
                            'fontWeight': '200',
                            'fontSize': '12px',
                            'fontFamily': "Lucida Sans Typewriter",
                        },
                    ),
                ])
            ]),

        ]
    )]
)


# callbacks
@callback(
    [
        Output('month-length', 'invalid'),
        Output('month-length', 'valid'),
    ],
    [
        Input('month-length', 'value'),
        Input('month-length', 'min'),
        Input('month-length', 'max'),
    ],
)
def update_input(value, minvalue, maxvalue):
    if value is not None:
        value = int(value)
        if minvalue <= value <= maxvalue:
            return False, True
    return True, False


@callback(
    Output('table', 'columns'),
    Input('month-length', 'value')
)
def update_table(value):
    if value is not None:
        current_date = datetime.now()
        start_date = current_date + timedelta(days=30)

        month_columns = []
        for _ in range(int(value)):
            month_columns.append(start_date.strftime("%m, %Y"))
            start_date = start_date + timedelta(days=30)

        columns = [
            {'name': 'Market', 'id': 'market'},
            {'name': 'Commodity', 'id': 'commodity'},
            *[
                {'name': month, 'id': month, 'type': 'numeric',
                'format': FormatTemplate.percentage(2)}
                for month in month_columns
            ],
        ]

    else:
        columns = [
            {'name': 'Market', 'id': 'market'},
            {'name': 'Commodity', 'id': 'commodity'},
        ]
    
    return columns

@callback(
    Output('table', 'data'),
    [
        Input('multiple-predict', 'n_clicks'),
        Input('select-market', 'value'),
        Input('select-commodity', 'value'),
        Input('month-length', 'value'),
        Input('table', 'columns'),
    ],
    State('table', 'data')
)
def update_table_values(n_clicks, markets, crops, months, table_columns, current_data):

    if n_clicks == 0:
        return current_data or []
    
    updated_data = current_data if current_data is not None else []

    month_year_columns = [col for col in table_columns if ',' in col['name']]

    for market in markets:
        for crop in crops:
            for month in range(int(months)):
                new_row = {
                    'market': market,
                    'commodity': crop,
                }

                for column in month_year_columns:
                    month, year = map(int, column['name'].split(', '))
                    new_row[column['id']] = predict_price(market, crop, year, month)
                
                updated_data.append(new_row)

    return updated_data
    
def predict_price(market, crop, year, month):

    column_order = [
        'market',
        'year',
        'month',
        'years_since_start',
        'past_1_months_mean_price',
        'past_2_months_mean_price',
        'past_3_months_mean_price',
        'past_4_months_mean_price',
        'past_5_months_mean_price',
        'past_6_months_mean_price',
        'past_7_months_mean_price',
        'past_8_months_mean_price',
        'past_9_months_mean_price',
        'past_10_months_mean_price',
        'past_11_months_mean_price',
        'past_1_years_mean_price',
        'past_2_years_mean_price',
        'past_3_years_mean_price',
        'past_4_years_mean_price',
        'past_5_years_mean_price',
        'past_6_years_mean_price',
        'past_7_years_mean_price',
        'past_8_years_mean_price',
        'past_9_years_mean_price',
        'past_10_years_mean_price',
        'past_11_years_mean_price',
        'past_12_years_mean_price',
        'past_13_years_mean_price',
        'past_14_years_mean_price',
        'past_15_years_mean_price',
        'past_16_years_mean_price',
        'past_17_years_mean_price',
        'yearly_average_price',
        'monthly_average_price',
        'market_average_price',
        'commodity_yearly_average_price',
        'commodity_monthly_average_price'
    ]

    market_mapping = {
        'Arusha (urban)': 0,
        'Babati': 1,
        'Bukoba': 2,
        'Dar es Salaam - Ilala': 3,
        'Dar es Salaam - Kinondoni': 4,
        'Dodoma (Kibaigwa)': 5,
        'Dodoma (Majengo)': 6,
        'Morogoro': 7,
        'Mpanda': 8,
        'Mtwara DC': 9,
        'Musoma': 10,
        'Tabora': 11,
        'Tanga / Mgandini': 12
    }

    inputDict = {}

    inputDict['market'] = market_mapping.get(str(market))

    inputDict['year'] = [int(year)]

    inputDict['month'] = [int(month)]

    inputDict['years_since_start'] = int(year) - 2006

    if crop == 'Maize':
        if str(market) not in Maize_data['market']:
            most_recent_year = int(year) - 3
        else:
            most_recent_year = int(year) - 1
        filtered_data = Maize_data[(Maize_data['market'] == market_mapping.get(str(market))) &
                                    (Maize_data['year'] == most_recent_year)]

        inputDict['yearly_average_price'] = filtered_data['yearly_average_price'].mode(
        )

        if int(month) in filtered_data['month'].unique():
            inputDict['monthly_average_price'] = filtered_data.loc[filtered_data['month'] == int(month)]['market_average_price'].reset_index(drop=True)
        else:
            inputDict['monthly_average_price'] = filtered_data['monthly_average_price'].mean(
            )

        inputDict['market_average_price'] = filtered_data['market_average_price'].mode(
        )

        inputDict['commodity_yearly_average_price'] = filtered_data['commodity_yearly_average_price'].mode()

        if int(month) in filtered_data['month'].unique():
            inputDict['commodity_monthly_average_price'] = filtered_data.loc[filtered_data['month'] == int(
                month)]['commodity_monthly_average_price'].reset_index(drop=True)
        else:
            inputDict['commodity_monthly_average_price'] = filtered_data['commodity_monthly_average_price'].mean(
            )

        filtered_data = filtered_data.drop(['market', 'year', 'month', 'years_since_start', 'yearly_average_price', 'monthly_average_price',
                                            'market_average_price', 'commodity_yearly_average_price', 'commodity_monthly_average_price'], axis=1)

        for col in filtered_data.columns:
            inputDict[col] = filtered_data[col].mean()

    elif crop == 'Beans':
        if str(market) not in Beans_data['market']:
            most_recent_year = int(year) - 3
        else:
            most_recent_year = int(year) - 1
        filtered_data = Beans_data[(Beans_data['market'] == market_mapping.get(str(market))) &
                                    (Beans_data['year'] == most_recent_year)]

        inputDict['yearly_average_price'] = filtered_data['yearly_average_price'].mode(
        )

        if int(month) in filtered_data['month'].unique():
            inputDict['monthly_average_price'] = filtered_data.loc[filtered_data['month'] == int(
                month)]['market_average_price'].reset_index(drop=True)
        else:
            inputDict['monthly_average_price'] = filtered_data['monthly_average_price'].mean(
            )

        inputDict['market_average_price'] = filtered_data['market_average_price'].mode(
        )

        inputDict['commodity_yearly_average_price'] = filtered_data['commodity_yearly_average_price'].mode()

        if int(month) in filtered_data['month'].unique():
            inputDict['commodity_monthly_average_price'] = filtered_data.loc[filtered_data['month'] == int(
                month)]['commodity_monthly_average_price'].reset_index(drop=True)
        else:
            inputDict['commodity_monthly_average_price'] = filtered_data['commodity_monthly_average_price'].mean(
            )

        filtered_data = filtered_data.drop(['market', 'year', 'month', 'years_since_start', 'yearly_average_price', 'monthly_average_price',
                                            'market_average_price', 'commodity_yearly_average_price', 'commodity_monthly_average_price'], axis=1)

        for col in filtered_data.columns:
            inputDict[col] = filtered_data[col].mean()

    elif crop == 'Rice':
        if str(market) not in Rice_data['market']:
            most_recent_year = int(year) - 3
        else:
            most_recent_year = int(year) - 1
        filtered_data = Rice_data[(Rice_data['market'] == market_mapping.get(str(market))) &
                                    (Rice_data['year'] == most_recent_year)]

        inputDict['yearly_average_price'] = filtered_data['yearly_average_price'].mode(
        )

        if int(month) in filtered_data['month'].unique():
            inputDict['monthly_average_price'] = filtered_data.loc[filtered_data['month'] == int(month)]['market_average_price'].reset_index(drop=True)
        else:
            inputDict['monthly_average_price'] = filtered_data['monthly_average_price'].mean(
            )

        inputDict['market_average_price'] = filtered_data['market_average_price'].mode(
        )

        inputDict['commodity_yearly_average_price'] = filtered_data['commodity_yearly_average_price'].mode()

        if int(month) in filtered_data['month'].unique():
            inputDict['commodity_monthly_average_price'] = filtered_data.loc[filtered_data['month'] == int(month)]['commodity_monthly_average_price'].reset_index(drop=True)
        else:
            inputDict['commodity_monthly_average_price'] = filtered_data['commodity_monthly_average_price'].mean(
            )

        filtered_data = filtered_data.drop(['market', 'year', 'month', 'years_since_start', 'yearly_average_price', 'monthly_average_price',
                                            'market_average_price', 'commodity_yearly_average_price', 'commodity_monthly_average_price'], axis=1)

        for col in filtered_data.columns:
            inputDict[col] = filtered_data[col].mean()


    dataFrame = pd.DataFrame(inputDict, columns=column_order)
    predicted_price = None

    if crop == 'Maize':
        json_data = dataFrame.to_json(orient='records')
        res = requests.post('https://crops-api.site.atomatiki.tech/predict-maize', json=json.loads(json_data)[
                            0], headers={'Content-Type': 'application/json', 'Content-Security-Policy': 'upgrade-insecure-requests'})
        predicted_price = res.json()

    elif crop == 'Beans':
        json_data = dataFrame.to_json(orient='records')
        res = requests.post('https://crops-api.site.atomatiki.tech/predict-beans', json=json.loads(json_data)[
                            0], headers={'Content-Type': 'application/json', 'Content-Security-Policy': 'upgrade-insecure-requests'})
        predicted_price = res.json()
    elif crop == 'Rice':
        json_data = dataFrame.to_json(orient='records')
        res = requests.post('https://crops-api.site.atomatiki.tech/predict-rice', json=json.loads(json_data)[
                            0], headers={'Content-Type': 'application/json', 'Content-Security-Policy': 'upgrade-insecure-requests'})
        predicted_price = res.json()

    if predicted_price is not None:
        return f'TZS {float(predicted_price):,.2f}'
    return 0.0