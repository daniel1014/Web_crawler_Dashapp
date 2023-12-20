import io
import base64
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State, ALL
from dash.dash_table import DataTable
from googlesearch import search
import pandas as pd
import json
import db_connection

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the app layout
app.layout = html.Div([
    html.H1("News Scraper"),
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
    html.Button('Save as Excel', id='save-button', n_clicks=0),
    html.Div(id='download-link-container'),
    html.A(id='download-link', download="output.xlsx", href="", target="_blank"),
    html.Div(id='all-results', style={'display': 'none'}),
    dcc.Store(id='all-results-store')
])

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
            if focus_input:
                query = supplier_input + " " + focus_input + " news"
            else:
                query = supplier_input + " news"
            search_results = search(query, advanced=True, lang='en', num_results=10)
            for result in search_results:
                if " — " in result.description:
                    date, description = result.description.split(" — ", 1)
                else:
                    date = ""
                    description = result.description
                all_results.append({'Supplier': supplier_input, 'Focus': focus_input, 'Title': result.title, 'Date' : date, 'Description': description, 'URL': result.url})
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

@app.callback(
    Output('download-link-container', 'children'),
    [Input('download-link', 'href')]
)
def update_download_link(href):
    if href != "":
        return html.A('Download Excel file', id='download-link', download="output.xlsx", href=href, target="_blank")

@app.callback(
    Output('download-link', 'href'),
    [Input('save-button', 'n_clicks')],
    [State('all-results-store', 'data')]
)

def generate_excel(n_clicks, all_results):
    if n_clicks > 0 and all_results is not None:
        df = pd.DataFrame(all_results)
        xlsx_io = io.BytesIO()
        writer = pd.ExcelWriter(xlsx_io, engine='xlsxwriter')
        df.to_excel(writer, sheet_name="Sheet1")
        writer.save()
        xlsx_io.seek(0)
        data = base64.b64encode(xlsx_io.read()).decode("utf-8")
        return f"data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{data}"
    
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