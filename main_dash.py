import dash
from dash import dcc
import dash_bootstrap_components as dbc
from dash import html
from dash.dependencies import Input, Output, State, ALL
from dash.dash_table import DataTable
from dash_ag_grid import AgGrid
import pandas as pd
import db_connection
import gsearch as s

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MORPH])
data_demo = [{'supplier':"Enercon",'focus':'Supply Chain','num_search':'10'}]
df_database_demo = pd.DataFrame(data_demo)
new_line = [{'supplier':'','focus':'','num_search':'10'}]
df_new_line = pd.DataFrame(new_line)

# Define the app layout
app.layout = dbc.Container([
    html.H1("News Scraper"),
    dcc.Download(id="download"),
    dbc.Row([
        dbc.Col([
            dbc.Input(id={'type':'supplier-input', 'index': 1}, type='text', placeholder="Enter Supplier", className='mb-2'),
        ],width=2),
        dbc.Col([
            dbc.Input(id={'type':'focus-input', 'index': 1}, type='text', placeholder="Enter Focus", className='mb-2'),
        ], width=2),
        ], id='input-container'),
    dbc.Row([
        dbc.Col([
            AgGrid(
                id="table_input",
                columnDefs=[
                    {
                        "headerName": "Supplier",
                        "field": "supplier",
                        "cellEditor": "agTextCellEditor",
                         "cellEditorParams": {
                         "maxLength": 20,
                        },
                    },
                    {
                        "headerName": "Focus",
                        "field": "focus",
                        "cellEditor": "agTextCellEditor",
                         "cellEditorParams": {
                         "maxLength": 20,
                        },
                    },
                    {
                        "headerName": "Number of Search",
                        "field": "num_search",
                        "cellEditor": "agSelectCellEditor",
                        "cellEditorParams": {
                            "values": [str(i) for i in range(5, 31, 5)]
                        },
                    },
                ],
                rowData=df_database_demo.to_dict("records"),
                columnSize="sizeToFit",
                defaultColDef={'editable': True, 'sortable': True, 'filter': True},
                style={'height': '200px'},
            )
        ])
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Button('Add Input', id='add-input-button', n_clicks=0, className='mb-2'),
            dbc.Button('Search', id='search-button', n_clicks=0, className='mb-2'),
            dbc.Button('Upload to AECOM Database', id='upload-button', n_clicks=0, className='mb-2'),
        ]),
    ]),
    dbc.Row(
        dbc.Col(
            DataTable(
                id='table',
                columns=[{"name": i, "id": i} for i in ['Supplier', 'Focus', 'Title', 'Date', 'Description', 'URL']],
                data=[],
                page_action='custom',
                page_current=0,
                page_size=10
            ), 
            id='output-container'
        )
    ),
    dbc.Row([
        dbc.Col(
            dcc.Dropdown(
                id='dropdown',
                options=[  
                    {"label": "Excel file", "value": "excel"},
                    {"label": "CSV file", "value": "csv"},
                ],
                placeholder="Choose download file type. Default is Excel format!",
            ),width=4,
        ),
        dbc.Col(
            dbc.Button('Download Result', id='save-button', n_clicks=0),
        width=2
        )
    ]),
    dcc.Store(id='all-results-store'),
], fluid=True)

# Callback to add input fields in AgGrid table
@app.callback(
    Output('table_input', 'rowData'),
    Input('add-input-button', 'n_clicks'),
    Input('table_input', 'rowData'),
    prevent_initial_call=True
)

def add_input(n_clicks, rows):
    df_input = pd.DataFrame(rows)
    if n_clicks > 0:
        df_input = pd.concat([df_input,df_new_line], ignore_index=True)
    return df_input.to_dict("records")

# Callback to update the page content
@app.callback(
    [Output('output-container', 'children'), Output('all-results-store', 'data')],
    [Input('search-button', 'n_clicks'),
     Input('table', 'page_current'),
     Input('table', 'page_size')],
    [State('table_input', 'rowData')]
)
def update_output(n_clicks, page_current, page_size, table_input_data):
    page_current = 0 if page_current is None else page_current
    page_size = 10 if page_size is None else page_size
    if n_clicks > 0:
        all_results = []
        for row in table_input_data:
            supplier_input = row['supplier']
            focus_input = row['focus']
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

# Callback to download the search results
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
    
# Callback to upload the search results to database
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
        return 'Upload to AECOM Database'
    
if __name__ == '__main__':
    app.run_server(debug=True)