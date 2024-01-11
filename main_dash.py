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
df_database_demo = pd.DataFrame(data_demo).reset_index()
new_line = [{'supplier':'','focus':'','num_search':'10'}]
# df_new_line = pd.DataFrame(new_line)

# Define the app layout
app.layout = dbc.Container([
    html.H1("News Scraper Tool (under development)"),
    dcc.Markdown('''This tool is used to scrape news from Google Search Engine. Please login with your username to load your historic input (a new username will be registered if it is not exisiting). Please enter your desired input query(s) including supplier, focus (eg. Enercon Supply Chain), and number of search. Once you click 'Search', an output table will be generated with the corresponding title, date, description and URL. The output can be downloaded as Excel or CSV file. The input can be uploaded to AECOM database.''', style={'font-size': '18px'}),
    dcc.Download(id="download"),
    dcc.Store(id='selected-rows-store', data=[]),
    dbc.Row([
        dbc.Col([
            dbc.Input(id='username', type='text', placeholder="Enter Your Username", className='mb-2')
            ],width=3),
        dbc.Col([
            dbc.Button('Login (load your data)', id='login-button', className='text-light bg-primary'),
            html.Div(id='login-status')  # Placeholder for the alert callback
            ])
        ]),
    dbc.Row([
        dbc.Col([
            AgGrid(
                id="table_input",
                columnDefs=[
                    {
                        "headerName": "Index", 
                        "field": "index",
                        'width':50,
                        "checkboxSelection": True,},
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
                            "values": [str(i) for i in range(5, 11, 5)]
                        },
                    },
                ],
                rowData=df_database_demo.to_dict("records"),
                columnSize="sizeToFit",
                defaultColDef={'editable': True, 'sortable': True, 'filter': True},
                style={'height': '200px'},
                dashGridOptions={"rowSelection": "multiple",},
            )
        ])
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Button('Add Input', id='add-input-button', className='bg-light'),
            dbc.Button('Delete Selected Row', id='delete-input-button', className='bg-light'),
            dbc.Button('Search', id='search-button', n_clicks=0, className='text-success-emphasis bg-light'),
            dbc.Button('Upload to AECOM Database', id='upload-button', className='text-warning-emphasis bg-light'),
            html.Div(id='upload-status')  # Placeholder for the alert callback
        ]),
    ]),
    dbc.Row(
        dbc.Col(
            DataTable(
                id='table_output',
                columns=[{"name": i, "id": i} for i in ['Supplier', 'Focus', 'Title', 'Date', 'Description', 'URL']],
                data=[],
                page_action='custom',
                page_current=0,
                page_size=10,
                style_cell={'textAlign': 'left'},
                style_data_conditional=[
                    {
                        'if': {'column_id': 'URL'},
                        'textDecoration': 'underline',
                        'cursor': 'pointer'
                    }
                ],
                tooltip_duration=None
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
            dbc.Button('Download Result', id='save-button', className='text-light bg-info'),
        width=2
        )
    ])
], fluid=True)

@app.callback(
    Output('selected-rows-store', 'data'),
    Input('table_input', 'selectedRows')
)
def update_selected_rows(selected):
    # if selected is None:
    #     raise dash.exceptions.PreventUpdate
    selected_store = selected
    print(selected_store)
    return selected_store

@app.callback(
    [Output('table_input', 'rowData'), Output('login-status', 'children')],
    [Input('login-button', 'n_clicks'),
    Input('add-input-button', 'n_clicks'),
    Input('delete-input-button', 'n_clicks')],
    [State('username', 'value'),
    State('table_input', 'rowData'),
    State('selected-rows-store', 'data')],
    prevent_initial_call=True
)
def update_table(login_clicks, add_input_clicks, delete_clicks, username, all_rows, selected_rows):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'login-button':
        try:
            df_database = db_connection.df_from_db(f"SELECT supplier, focus, num_search FROM BMT.NewsInput WHERE username = '{username}'")
            df_database = df_database.reset_index(drop=True)
            df_database['index'] = df_database.index
            return df_database.to_dict("records"), dbc.Alert("Login Successful", duration=3000, class_name="alert-success")
        except Exception as e:
            return [], dbc.Alert(f"Login Failed. Error details:{str(e)}", class_name="alert-warning")
    elif button_id == 'add-input-button':
        df_input = pd.DataFrame(all_rows)
        df_input = df_input.reset_index(drop=True)
        if df_input.empty:
            df_new_input = pd.DataFrame(new_line, index=[0]).reset_index()
        else:
            df_new_input = pd.DataFrame(new_line, index=[df_input['index'].max() + 1]).reset_index()
        df_input = pd.concat([df_input,df_new_input], ignore_index=True)
        return df_input.to_dict("records"), dash.no_update
    elif button_id == 'delete-input-button':
        df_input = pd.DataFrame(all_rows)
        selected_rows = [row['index'] for row in selected_rows]
        df_input = df_input[~df_input['index'].isin(selected_rows)]
        df_input.reset_index(drop=True,inplace=True)
        df_input['index'] = df_input.index
        return df_input.to_dict('records'), dash.no_update

# Callback to update the page content
@app.callback(
    [Output('table_output', 'data'), Output('table_output', 'tooltip_data')],
    [Input('search-button', 'n_clicks'),
     Input('table_output', 'page_current'),
     Input('table_output', 'page_size')],
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
            num_search = int(row['num_search'])
            query = supplier_input + " " + focus_input 
            search_results = s.google_search(query, s.my_api_key, s.my_cse_id, num=num_search)
            for result in search_results:
                if " ... " in result['snippet']:
                    date, description = result['snippet'].split(" ... ", 1)
                else:
                    date = ""
                    description = result['snippet']
                all_results.append({'Supplier': supplier_input, 'Focus': focus_input, 'Title': result['title'], 'Date' : date, 'Description': description, 'URL': result['link']})
        page_start = page_current * page_size
        page_end = page_start + page_size
        tooltip_data=[
            {
                column: {'value': str(value), 'type': 'markdown'}
                for column, value in row.items()
            } for row in all_results
        ]
        return all_results[page_start:page_end], tooltip_data
    else:
        return [], []   # Default return value

# Callback to download the search results
@app.callback(
    Output('download', 'data'),
    [Input('save-button', 'n_clicks')],
    [State('table_output', 'data'),
     State('dropdown', 'value')],
     prevent_initial_call=True
)

def generate_excel(n_clicks, all_results, download_type):
    df = pd.DataFrame(all_results)
    if download_type == "csv":
        return dcc.send_data_frame(df.to_csv, "news_output.csv")
    else:
        return dcc.send_data_frame(df.to_excel, "news_output.xlsx", sheet_name="news_output", index=False)
    
# Callback to upload the search input to database
@app.callback(
    Output('upload-status', 'children'),
    [Input('upload-button', 'n_clicks')],
    [State('table_input', 'rowData'), State('username', 'value')],
    prevent_initial_call=True
)
def upload_to_database_input(n_clicks, table_input_data, username):
    if n_clicks > 0:
        try:
            db_connection.upload_data(table_input_data, 'NewsInput', username) 
            return dbc.Alert("Upload Successful", duration=3000, class_name="alert-success")
        except Exception as e:
            return dbc.Alert(f"Upload Failed. Error details:{str(e)}", class_name="alert-warning")
    else:
        return None
    
if __name__ == '__main__':
    app.run_server(debug=True)