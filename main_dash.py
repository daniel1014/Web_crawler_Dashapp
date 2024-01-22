import dash
from dash import html, dcc, ctx 
from dash.dependencies import Input, Output, State, ALL
from dash.dash_table import DataTable
from dash_ag_grid import AgGrid
import dash_bootstrap_components as dbc
import pandas as pd
import db_connection
import gsearch as s
import sentiment_analysis 
import plotly.express as px 

# Initialize the Dash app

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP])
data_demo = [{'supplier':"Enercon",'focus':'Supply Chain','num_search':'10'}]
df_database_demo = pd.DataFrame(data_demo).reset_index()
new_line = [{'supplier':'','focus':'','num_search':'10'}]

# Define the app layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.Img(src='/assets/AECOM_Logo_Black_RGB.png', height="60px"),width="3"),
        dbc.Col(html.H1("News Scraper Tool (under development)"), align="center")
    ], align="center", style={'background-color': '#C4C4C4'}),
    dcc.Markdown('''
                 * ##### This tool is used to scrape news from Google Search Engine. Please **Login** with your username to load your historic input data (a new username will be registered if it is not exisiting in database). 
                 * ##### Please enter your desired input query(s) including supplier, focus (eg. Enercon Supply Chain), and number of search. 
                 * ##### When you're ready, click **'Search'** and an output table will be generated along with the tabs corresponding to your choice of input above. 
                 * ##### Next, click **'Sentiment Analysis'** and views the related results from the bar chart. 
                 * ##### If you want to save the current input(s) into the database, click **"Uploaded Input to AECOM database"** so you can download your data with your unique username when you are back next time. Furthermore, both the news output and sentiment analysis results can be downloaded as Excel or CSV file. 
                 ''', ),
    dcc.Download(id="download-news-output"),
    dcc.Download(id="download-sentiment-output"),
    dcc.Store(id='selected-rows-store', data=[]),   # Store the selected rows 
    dcc.Store(id='news-output-store'),         # Store the news output for download
    dcc.Store(id='sentiment-output-store'),    # Store the sentiment output for download
    dcc.Store(id='topics-output-store'),       # Store the topics output for download
    dbc.Row([
        dbc.Col([
            dbc.Input(id='username', type='text', placeholder="Enter Your Username", className='mb-2')
            ],width=3),
        dbc.Col([
            dbc.Button('Login (to load your data)', id='login-button', style={'background-color':'#AECC53','font-size': '19px', 'font-weight':'600'}, className='text-dark'),
            ],width='auto'),
        dbc.Col([
            html.Div(id='login-status')  # Placeholder for the alert callback
            ],width=7)
        ]),
    dbc.Row([
        dbc.Col([
            dbc.Button(['[+] Add Input'], id='add-input-button', className='text-info-emphasis bg-light', style={'margin-top': '10px'}),
            dbc.Button('[-] Delete Selected Row', id='delete-input-button', className='text-info-emphasis bg-light', style={'margin-top': '10px'})
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
    dbc.Col(
        dbc.Button([html.I(className="bi bi-send"),' Search'], id='search-button', size="lg", style={'background-color':'#009A9B','font-size': '19px', 'border-radius': '10px','font-weight':'600','padding':'20px'}),
        width="auto"
    ),
    dbc.Col(
        dbc.Button([html.I(className="bi bi-bar-chart"),' Sentiment Analysis'], id='sentiment-button', style={'background-color':'#009A9B','font-size': '19px', 'border-radius': '10px','font-weight':'600', 'padding':'20px'}),
        width="auto"
    ),
    dbc.Col(
        dbc.Button([html.I(className="bi bi-lightbulb"),' Topics Analysis (Wordcloud)'], id='topics-button', style={'background-color':'#009A9B','font-size': '19px', 'border-radius': '10px','font-weight':'600', 'padding':'20px'}),
        width="auto"
    ),
    ], justify="center", style={'margin-top': '15px'}),
    dcc.Loading(id="Loading", type="cube", children=[html.Div(id='tabs-content')]),
    dcc.Tabs(id='tabs',className='custom-tabs-container', value='tab-1'),
    html.Hr(style={"height":"2px","border-width":"0","color":"gray","background-color":"gray"}),
    dbc.Row([
        dbc.Col([
            dbc.Button([html.I(className="bi bi-database-up"),' Upload Input to AECOM Database'], 
                        id='upload-button', 
                        className='text-info-emphasis bg-light',
                        style={"margin-bottom": "20px"},
                        )],
        width=2),
        dbc.Col([
            html.Div(id='upload-status')  # Placeholder for the alert callback
        ],width=10),
    ]),
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
        dbc.Col([
            dbc.Button([html.I(className="bi bi-download"),' Download News Output'], id='save-button-news', className='text-black bg-light'),
            dbc.Button([html.I(className="bi bi-download"),' Download Sentiment Analysis Output'], id='save-button-sentiment', className='text-black bg-light'),],
        width=8
        ),
    ]),
], fluid=True, style={'background-color': '#F1F1F1'})

# Callback to update the selected rows
@app.callback(
    Output('selected-rows-store', 'data'),
    Input('table_input', 'selectedRows'),
    prevent_initial_call=True
)
def update_selected_rows(selected):
    selected_store = selected
    return selected_store

# Callback to update the input table
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
def update_input(login_clicks, add_input_clicks, delete_clicks, username, all_rows, selected_rows):
    button_id = ctx.triggered_id    # can use dash.callback_context for dash version > 1.16.0

    if button_id == 'login-button':
        if username is None or username == "":
            return [], dbc.Alert("Please enter your username!", class_name="text-white", style={'background-color':'#E52713', 'font-weight':'600'}, duration=4000)
        try:
            df_database = db_connection.df_from_db(f"SELECT supplier, focus, num_search FROM BMT.NewsInput WHERE username = '{username}'")
            df_database = df_database.reset_index(drop=True)
            df_database['index'] = df_database.index
            return df_database.to_dict("records"), dbc.Alert([html.I(className="bi bi-check-circle-fill me-2")," Login Successful"], duration=3000, class_name="text-dark", style={'background-color':'#AECC53', 'font-weight':'600'})
        except Exception as e:
            return [], dbc.Alert(f"Login Failed. Error details:{str(e)}", class_name="text-dark", style={'background-color':'#FFCE00', 'font-weight':'600'})
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

# Callback to update the output table
@app.callback(
    [Output('tabs','children'),
     Output('tabs-content', 'children'), 
     Output('news-output-store', 'data'), 
     Output('sentiment-output-store', 'data'),
     Output('topics-output-store', 'data')],
    [Input('search-button', 'n_clicks'),
     Input('sentiment-button', 'n_clicks'),
     Input('topics-button', 'n_clicks')],
    [State('table_input', 'rowData'),
     State('news-output-store', 'data')],
    prevent_initial_call=True
)
def update_output(n_clicks, n_clicks_s, n_clicks_s_s, table_input_data, news_output_data):
    all_results = []
    sentiment_input = {}
    tabs = []
    # Search Results
    if ctx.triggered_id == 'search-button':
        for row in table_input_data:
            supplier_input = row['supplier']
            focus_input = row['focus']
            num_search = int(row['num_search'])
            query = supplier_input + " " + focus_input
            tab_label = f"{supplier_input} - {focus_input}"         # Create tab label dynamically
            tabs.append(dcc.Tab(label=tab_label, value=tab_label+"-table", className='text-primary-emphasis bg-white strong'))  # Add tab dynamically
            search_results = s.google_search(query, num=num_search)
            for result in search_results:
                if " ... " in result['snippet']:
                    date, description = result['snippet'].split(" ... ", 1)
                else:
                    date = ""
                    description = result['snippet']
                all_results.append({'Supplier': supplier_input, 'Focus': focus_input, 'Title': result['title'], 'Date' : date, 'Description': description, 'URL': result['link']})
        return tabs, DataTable(
            id='table_output',
            columns=[{"name": i, "id": i} for i in ['Supplier', 'Focus', 'Title', 'Date', 'Description', 'URL']],
            data=all_results[0:10],
            # page_action='native',
            # page_current=0,
            # page_size=10,
            style_cell={'textAlign': 'left'},
            style_cell_conditional=[
                {'if': {'column_id': 'Description'}, 'maxWidth': '700px'},  # Set width for Description column
                {'if': {'column_id': 'URL'}, 'textDecoration': 'underline', 'cursor': 'pointer'}
            ],
            tooltip_duration=None,
            tooltip_data=[
            {column: {'value': str(value), 'type': 'markdown'} for column, value in row.items()}
            for row in all_results
            ]     
        ), all_results, dash.no_update, dash.no_update
    elif ctx.triggered_id == 'sentiment-button':
        # Sentiment Analysis 
        if news_output_data is None:
            return dash.no_update, dbc.Alert([html.I(className="bi bi-exclamation-triangle-fill me-2")," Please click 'Search' button first to generate the news output!"], class_name="text-dark", style={'background-color':'#FFCE00', 'font-weight':'600'}, duration=4000), dash.no_update, dash.no_update, dash.no_update
        for row in news_output_data:
            sentiment_input[row['Supplier']+" "+row['Focus']] = [] if row['Supplier']+" "+row['Focus'] not in sentiment_input else sentiment_input[row['Supplier']+" "+row['Focus']]
            sentiment_input[row['Supplier']+" "+row['Focus']].append({row['Title']:row['Description'][:-4]})
        sentiment_result = sentiment_analysis.sentiment_analysis(sentiment_input)
        df_sentiment_result = pd.DataFrame(sentiment_result).T
        fig = px.bar(df_sentiment_result, x=df_sentiment_result.columns, y=df_sentiment_result.index, orientation='h', title='Sentiment Analysis Results', text_auto=True, labels={'value':'Sentiment Distribution', 'index':'Supplier Focus', 'variable':'Emotion'},  color_discrete_map={'positive':'#AECC53', 'neutral':'#DAD8CC', 'negative':'#C70C6F'})
        return tabs, dcc.Graph(figure=fig), all_results, sentiment_result, dash.no_update
    elif ctx.triggered_id == 'topics-button':
        if news_output_data is None:
            return dash.no_update, dbc.Alert([html.I(className="bi bi-exclamation-triangle-fill me-2")," Please click 'Search' button first to generate the news output!"], class_name="text-dark", style={'background-color':'#FFCE00', 'font-weight':'600'}, duration=4000), dash.no_update, dash.no_update, dash.no_update
         # Add tab dynamically
        for row in table_input_data:
            supplier_input = row['supplier']
            focus_input = row['focus']
            tab_label = f"{supplier_input} - {focus_input}"         # Create tab label dynamically
            tabs.append(dcc.Tab(label=tab_label, value=tab_label+"-wordcloud", className='text-primary-emphasis bg-white strong')) 
        for row in news_output_data:
            sentiment_input[row['Supplier']+" - "+row['Focus']] = [] if row['Supplier']+" "+row['Focus'] not in sentiment_input else sentiment_input[row['Supplier']+" "+row['Focus']]
            sentiment_input[row['Supplier']+" - "+row['Focus']].append({row['Title']:row['Description'][:-4]})
        topics_result = sentiment_analysis.topics_analysis(sentiment_input) 
        print(list(topics_result.keys())[0])
        sentiment_analysis.create_wordcloud_animation(topics_result)
        return tabs, html.Div([html.Img(src='/assets/animation.gif')], style={'display': 'flex', 'justify-content': 'center'}), all_results, dash.no_update, topics_result

@app.callback(
    Output('tabs-content', 'children', allow_duplicate=True),
    Input('tabs', 'value'),
    State('news-output-store', 'data'),
    prevent_initial_call=True
)
def render_content_tabs(tabs, table_data):
    if tabs != "tab-1" and 'table' in tabs:             # tab-1 is the default tab at the initial load of the app
        # Filter the table data based on the selected tab
        tabs = tabs.replace("-table", "")               # Remove the '-table' suffix from the tab label
        supplier, focus =  tabs.split(' - ')
        print(supplier, focus)
        filtered_data = [row for row in table_data if row['Supplier'] == supplier and row['Focus'] == focus]
        return DataTable(
            id='table_output',
            columns=[{"name": i, "id": i} for i in ['Supplier', 'Focus', 'Title', 'Date', 'Description', 'URL']],
            data=filtered_data,
            style_cell={'textAlign': 'left'},
            style_cell_conditional=[
                {'if': {'column_id': 'Description'}, 'width': '25px'},  # Set width for Description column
                {'if': {'column_id': 'URL'}, 'textDecoration': 'underline', 'cursor': 'pointer'}
            ],
            tooltip_duration=None,
            tooltip_data=[
            {column: {'value': str(value), 'type': 'markdown'} for column, value in row.items()}
            for row in filtered_data
            ]     
        )

# Callback to download the News Output
@app.callback(
    Output('download-news-output', 'data'),
    [Input('save-button-news', 'n_clicks')],
    [State('news-output-store', 'data'),
     State('dropdown', 'value')],
     prevent_initial_call=True
)
def generate_excel(n_clicks, all_results, download_type):
    df = pd.DataFrame(all_results)
    if download_type == "csv":
        return dcc.send_data_frame(df.to_csv, "news_output.csv")
    else:
        return dcc.send_data_frame(df.to_excel, "news_output.xlsx", sheet_name="news_output", index=False)
    
# Callback to download the Sentiment Analysis Results
@app.callback(
    Output('download-sentiment-output', 'data'),
    [Input('save-button-sentiment', 'n_clicks')],
    [State('sentiment-output-store', 'data'),
     State('dropdown', 'value')],
     prevent_initial_call=True
)
def generate_excel(n_clicks, sentiment_output, download_type):
    df = pd.DataFrame(sentiment_output).T.reset_index().rename(columns={'index':'Supplier Focus'})
    if download_type == "csv":
        return dcc.send_data_frame(df.to_csv, "sentiment_analysis_output.csv")
    else:
        return dcc.send_data_frame(df.to_excel, "sentiment_analysis_output.xlsx", sheet_name="news_output", index=False)
    
# Callback to upload the search input to database
@app.callback(
    Output('upload-status', 'children'),
    [Input('upload-button', 'n_clicks')],
    [State('table_input', 'rowData'), State('username', 'value')],
    prevent_initial_call=True
)
def upload_to_database_input(n_clicks, table_input_data, username):
    if username is None or username == "":
        return dbc.Alert("Please enter your username!", class_name="text-light", style={'background-color':'#E52713', 'font-weight':'600'}, duration=4000)
    try:
        db_connection.upload_data(table_input_data, 'NewsInput', username) 
        return dbc.Alert([html.I(className="bi bi-check-circle-fill me-2")," Upload Successful"], duration=3000,  class_name="text-dark", style={'background-color':'#AECC53', 'font-weight':'600'})
    except Exception as e:
        return dbc.Alert(f"Upload Failed. Error details:{str(e)}", class_name="text-light alert-warning",style={'background-color':'#E52713', 'font-weight':'600'})
    
if __name__ == '__main__':
    app.run_server(debug=True)