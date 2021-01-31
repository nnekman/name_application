# -*- coding: utf-8 -*-
"""
Created on Tue Jan 26 19:14:27 2021

@author: nnekman
"""
# %%

import dash
import dash_table
import pandas as pd
import json
import urllib

import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

# %% ---------------------------------------------------------------------------------------------------------
# %% Helper functions

def update_table(df):
    print('>>>> update_table function executed')

    if df is  None:
        default_data = {'Names': ['names'], 'Amounts': ['amounts']}
        df = pd.DataFrame(data=default_data)

    table = dash_table.DataTable(id="data_table",
                         columns=[{"name": i, "id": i} for i in df.columns],
                         style_table = {'maxHeight': '300px','overflowY': 'scroll'},
                         style_header={'backgroundColor': 'rgb(230, 230, 230)','fontWeight': 'bold'},
                         style_cell_conditional=[{ 'if': {'column_id': c}, 'textAlign': 'center'} for c in df.columns],
                         style_data_conditional=[{ 'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}],
                         data=df.to_dict('records')
    )
    return table

def order_table(name,word):
    print('>>>> reorder data function executed')
    
    df = pd.read_json(name,orient='split')
    if 'abc' in word:
        ordered_df=df.sort_values('name')
        print(ordered_df)
    if 'amount' in word:
        ordered_df=df.sort_values('amount',ascending=False)
        print(ordered_df) 
    return ordered_df.to_json(orient='split')

# %% ---------------------------------------------------------------------------------------------------------
# %% Style sheet (dark is nice)

external_stylesheets=[dbc.themes.SOLAR]

# %%
page_title_text = 'Name Application Version 0.1'
html_link = 'https://plot.ly'
PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

# %% Defining application
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config.suppress_callback_exceptions = True # Dynamic elements, avoid error messages

# %% ---------------------------------------------------------------------------------------------------------
# %% Nav bar

logo_col =  dbc.Col(html.Img(src=PLOTLY_LOGO, height="30px"))
brand_col = dbc.Col(dbc.NavbarBrand(page_title_text, className="ml-2"))

brand_elements = dbc.Row(id = 'brand_elements',children = [logo_col, brand_col],align="center",no_gutters=True)
brand_component = html.A(id='brand_component',children = brand_elements, href=html_link)

upload_button = dcc.Upload(id='upload_file',children=[dbc.Button('Upload JSON File', color="primary", className="mr-1")])
upload_container = html.Div(id='upload_file_container',children = upload_button)
upload_component = dbc.Row(children = upload_container,no_gutters=True,className="ml-auto flex-nowrap mt-3 mt-md-0",align="center")

nav_chilren = [brand_component,upload_component]
navigation_bar = dbc.Navbar(children = nav_chilren, color="dark",dark=True)

# %% Build data table

table_collapse_button =  dbc.Button('Show Table',id='table_collapse_button', color='secondary',block=True, size='sm')
table_collapse_component =  dbc.Collapse(update_table(None),id="table_collapse")
table_collapse_children = [table_collapse_button,table_collapse_component]
table_collapse_div = html.Div(children=table_collapse_children, id='data_table_container',style={'padding': 6})

# %% Buttons

download_button = dbc.Col(dbc.Button('Download table in csv file',id='download_button', color='primary',style={'visibility':'hidden'},disabled=True,outline=True, size='sm'),width=2)
download_link = dbc.Col(html.A(download_button,id='download_link',download="name_data.csv",href="",target="_blank",style={'text-decoration':'none'}))

amount_names_label =  dbc.Button('Total amount of names: 0',id='names_label', color='transparent', size='md',style={'visibility':'hidden'},block=True,disabled=True)

label_button = dbc.Button('Order the table:',id='label_button', color='transparent', size='lg',style={'visibility':'hidden'},block=True,disabled=True)

default_button =  dbc.Col(dbc.Button('Default',id='default_button', color='success', size='md',style={'visibility':'hidden'},block=True),width=4)
abc_button =  dbc.Col(dbc.Button('Alphabetical',id='abc_button', color='success', size='md',style={'visibility':'hidden'},block=True),width=4)
amount_button =  dbc.Col(dbc.Button('Amount',id='amount_button', color='success', size='md',style={'visibility':'hidden'},block=True),width=4)

button_row = dbc.Row(children = [default_button,abc_button,amount_button],className="ml-auto flex-nowrap mt-3 mt-md-0",align="center")

# %% Error message for wrong kind of file

error_message = dbc.Alert("Your data type is not correct!", id='error_message', color="warning")

# %% Combine elements
separator = html.Div(style={'padding': 5})

common_table_row = dbc.Row(dbc.Col(dcc.Loading([table_collapse_div],type='circle')),id='table_row',style={'visibility':'visible'})
common_elements = [common_table_row,separator,amount_names_label,download_link,separator,label_button,separator,button_row]
common_layout = dbc.Container(common_elements,fluid = False, style={'padding': 20})

# %% global params

ids = ['df_full','df_order','names_amount','download_data']
common_globals=[html.Div(id=i,style={'display':'none'}) for i in ids]
global_data = dbc.Container(common_globals)

# %% Combine all to one; The layout

app.layout = html.Div([navigation_bar,common_layout,global_data,error_message])


# %% ---------------------------------------------------------------------------------------------------------
# %% Table collapse handling

@app.callback(
    Output("table_collapse", "is_open"),
    [Input("table_collapse_button", "n_clicks")],
    [State("table_collapse", "is_open")],)
def table_collapse(n_clicks, is_open):
    print(f'table_collapse fired: {n_clicks}, {is_open}')
    if n_clicks:
        return not is_open
    return is_open

@app.callback(
    Output("table_collapse_button", "children"),
    [Input("table_collapse", "is_open")])
def table_collapse_button_label(is_open):
    label = 'Hide Table' if(is_open == True) else 'Show Table'
    return label

# %% Upload file 

o_styles=['table_row','names_label','label_button','abc_button','default_button','amount_button','download_button']
outputs=[Output(i,'style') for i in o_styles]
outputs.extend([Output(i,'children') for i in ['df_full','names_amount','names_label']])
outputs.extend([Output('error_message','is_open'),Output('download_button','disabled')])

@app.callback(
    outputs,
    [Input('upload_file','contents')],
    [State('upload_file', 'filename')])
def upload_inputfile(file_content, file_name):
    ctx = dash.callback_context
   
    if not ctx.triggered:
        style={'visibility':'hidden'}
        return style,style,style,style,style,style,style,None,0,'Total amount of names: 0',False,True
    else:
        input_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if input_id == 'upload_file':
        if 'json' not in file_name:
            print(f'upload_inputfile fired: {input_id} - {file_name} - WRONG DATA TYPE.')
            error= True
            df_json = None
            style = {'visibility':'hidden'} 
            label_style=style
            names_total=0
            
        elif file_content is not None:
            print(f'upload_inputfile fired: {input_id} - {file_name}')

            df = pd.read_json(file_name,orient='records')
            
            #check there are 'name' and 'amount' 
            if 'name' not in df.iloc[0].values[0] or 'amount' not in df.iloc[0].values[0]:
                print(f'upload_inputfile fired: {input_id} - {file_name} - DOES NOT CONTAIN RIGHT ATTRIBUTES.')
                error= True
                df_json = None
                style = {'visibility':'hidden'} 
                label_style=style
                names_total=0

            # Put data in nicer form
            else:
                cleaned=pd.DataFrame()
                names=[]
                amounts=[]
                for i in range(len(df)):
                    val=df.iloc[i].values
                    names.append(val[0]['name'])
                    amounts.append(val[0]['amount'])
                cleaned['name']=names
                cleaned['amount']=amounts
            
                names_total=cleaned['amount'].sum()
            
                print(cleaned)
            
                df_json = cleaned.to_json(orient='split')    # must be json
                style = {'visibility':'visible'}
                label_style={'background-color': 'transparent','visibility':'visible'}
                error= False

        else:
            print(f'upload_inputfile fired: {input_id} - no file selcted')
            df_json = None
            style = {'visibility':'hidden'} 
            label_style=style
            names_total=0
            error = False
        download=False if names_total>0 else True
    
    return style,label_style,label_style,style,style,style,style,df_json,names_total,['Total amount of names: ',names_total],error,download

# %% Order buttons

@app.callback(
    [Output('abc_button','disabled'),Output('default_button','disabled'),Output('amount_button','disabled'),Output('df_order','children')],
    [Input('abc_button','n_clicks'),Input('default_button','n_clicks'),Input('amount_button','n_clicks')],
    [State('df_full','children')]
    )
def order_buttons(abc_clicks,default_clicks,amount_clicks,df):
    print('order buttons triggered')
    ctx = dash.callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if 'abc' in input_id:
        return True,False,False,order_table(df,'abc')
    elif 'default' in input_id:
        return False,True,False,df
    elif 'amount' in input_id:
        return False,False,True,order_table(df,'amount')
    return False,False,False,df

# %% Update table

@app.callback(
    Output('table_collapse','children'),
    [Input('df_full','children'),Input('df_order','children')]
    )
def table_update(df,ordered_df):
    print('fill in the values in the table')
    ctx = dash.callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if 'order' in input_id and ordered_df is not None: 
        data=pd.read_json(ordered_df,orient='split')
        return update_table(data)
    elif 'full' in input_id and df is not None: 
        data=pd.read_json(df,orient='split')
        return update_table(data)
    return None

# %% Download table in csv file 
 
@app.callback(
    Output('download_link', 'href'),
    #[Input('download_data','children')],
    [Input('df_order','children'),Input('df_full','children')])
def download_link(df_order,df_full):
    print('download_file fired')
    df=pd.read_json(df_full,orient='split') if df_full is not None else pd.DataFrame()
    df=pd.read_json(df_order,orient='split') if df_order is not None else df
    csv_string = df.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string


# %% ---------------------------------------------------------------------------------------------------------
# %%

if __name__ == '__main__':
    app.run_server(debug=True)
    