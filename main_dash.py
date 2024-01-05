import io
import base64
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State, ALL
from dash.dash_table import DataTable
from googlesearch import search
import pandas as pd
import db_connection
import gsearch as s
import dash_bootstrap_components as dbc

# Initialize the Dash app
sheet=['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=sheet)

# Define the app layout
app.layout = html.Div([
    html.H1("News Scraper"),
    dcc.Download(id="download"),
    html.Div(id='input-container', children=[
        dcc.Input(id={'type':'supplier-input', 'index': 1}, type='text', placeholder="Enter Supplier"),
        dcc.Input(id={'type':'focus-input', 'index': 1}, type='text', placeholder="Enter Focus"),
    ]),
    html.Button('Add Input', id='add-input-button', n_clicks=0),
    html.Button('Search', id='search-button', n_clicks=0),
    html.Button('Upload to Database', id='upload-button', n_clicks=0),
    html.Div(
        DataTable(
            id='table',
            columns=[{"name": i, "id": i} for i in ['Supplier', 'Focus', 'Title', 'Date', 'Description', 'URL']],
            data=[],
            page_action='custom',
            page_current=0,
            page_size=10
        ), 
        id='output-container'
    ),
    html.Div([
    dcc.Dropdown(
        id='dropdown',
        options=[  
        {"label": "Excel file", "value": "excel"},
        {"label": "CSV file", "value": "csv"},
        ],
        placeholder="Choose download file type. Default is Excel format!",
        style={'width': '50%', 'margin-right': '0px'},
        ),
    html.Button('Download Result', id='save-button', n_clicks=0)
],style={'display': 'flex', 'align-items': 'left'}),
    dcc.Store(id='all-results-store'),
],style={"margin": 30})

# Callback to dynamically add input fields
@app.callback(
    Output('input-container', 'children'),
    [Input('add-input-button', 'n_clicks')],
    [State('input-container', 'children')]
)

def add_input(n_clicks, current_children):
    if n_clicks > 0:
        new_input = html.Div([
            dcc.Input(id={'type': 'supplier-input', 'index': n_clicks + 1}, type='text', placeholder="Enter Supplier"),
            dcc.Input(id={'type': 'focus-input', 'index': n_clicks + 1}, type='text', placeholder="Enter Focus"),
        ])
        current_children.append(new_input)
    return current_children

# Callback to update the page content
@app.callback(
    [Output('output-container', 'children'), Output('all-results-store', 'data')],
    [Input('search-button', 'n_clicks'),
     Input('table', 'page_current'),
     Input('table', 'page_size')],
    [State({'type': 'supplier-input', 'index': ALL}, 'value'),
     State({'type': 'focus-input', 'index': ALL}, 'value')]
)
def update_output(n_clicks, page_current, page_size, supplier_inputs, focus_inputs):
    page_current = 0 if page_current is None else page_current
    page_size = 10 if page_size is None else page_size
    if n_clicks > 0:
        all_results = []
        for supplier_input, focus_input in zip(supplier_inputs, focus_inputs):
            query = supplier_input + " " + focus_input 
            search_results = s.google_search(query, s.my_api_key, s.my_cse_id, num=10)
            for result in search_results:
                if " ... " in result['snippet']:
                    date, description = result['snippet'].split(" ... ", 1)
                else:
                    date = ""
                    description = result['snippet']
                all_results.append({'Supplier': supplier_input, 'Focus': focus_input, 'Title': result['title'], 'Date' : date, 'Description': description, 'URL': result['link']})
        page_start = page_current * page_size
        page_end = page_start + page_size
        
        return DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in ['Supplier', 'Focus', 'Title', 'Date', 'Description', 'URL']],
        data=all_results[page_start:page_end],
        page_action='custom',
        page_current=page_current,          # Not constant, it would change when clicking on next/previous page
        page_size=page_size,                # constant value
        style_cell={'textAlign': 'left'},
        style_data_conditional=[
            {
                'if': {'column_id': 'URL'},
                'textDecoration': 'underline',
                'cursor': 'pointer'
            }
        ],
        tooltip_data=[
            {
                column: {'value': str(value), 'type': 'markdown'}
                for column, value in row.items()
            } for row in all_results
        ],
        tooltip_duration=None
        ), all_results
    else:
        return DataTable(id='table'), []   # Default return value

# @app.callback(
#     Output('download-link-container', 'children'),
#     [Input('download-link', 'href')]
# )
# def update_download_link(href):
#     if href != "":
#         return html.A('Download Excel file', id='download-link', download="output.xlsx", href=href, target="_blank")

@app.callback(
    Output('download', 'data'),
    [Input('save-button', 'n_clicks')],
    [State('all-results-store', 'data'),
     State('dropdown', 'value')],
     prevent_initial_call=True
)

def generate_excel(n_clicks, all_results, download_type):
    df = pd.DataFrame(all_results)
    if download_type == "csv":
        return dcc.send_data_frame(df.to_csv, "news_output.csv")
    else:
        return dcc.send_data_frame(df.to_excel, "news_output.xlsx", sheet_name="news_output", index=False)
    
# Add this callback function
@app.callback(
    Output('upload-button', 'children'),
    [Input('upload-button', 'n_clicks')],
    [State('all-results-store', 'data')]
)
def upload_to_database(n_clicks, all_results):
    if n_clicks > 0:
        db_connection.store_results(all_results)
        return 'Upload Successful'
    else:
        return 'Upload to Database'
    
if __name__ == '__main__':
    app.run_server(debug=True)