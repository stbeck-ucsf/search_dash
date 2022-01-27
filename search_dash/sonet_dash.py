# %%
# dash libs
import dash
import dash_bootstrap_components as dbc
import plotly.express as px
from dash import Input, Output, dcc, html
from dash_extensions import Mermaid
from tableone import TableOne

# data libs
import pandas as pd
from mcr_toolkit.dataset_tools import create_mysql_db_engine

# %%
# Data Manipulation

## Fetch data
mysql = create_mysql_db_engine('raw_sonet', './config/config.json')
tables = ['baseline','hhmembers','households','labreqfield']

df = dict()
for table in tables:
   df[table] = pd.read_sql_table(table, mysql)

# %%
df_baseline = df['baseline']

# %%
## Get total number screened.
num_screened = df_baseline.shape[0]

# %%
## Get total number who consented.
num_consent = df_baseline[df_baseline['consent'] == '1'].shape[0]

# %%
## Get the number who actively declined consent.
num_no_consent = df_baseline[df_baseline['consent'] == '2'].shape[0]

# %%
## Get percentage screened who have consented.
percent_consent = "{:.0%}".format(num_consent/num_screened)

# %%
## Get count for each screened participant.
df_baseline['starttime'] = pd.to_datetime(df_baseline['starttime'])

# %%
df_baseline_date = df_baseline.sort_values(by='starttime')

# %%
df_baseline_date['one'] = 1

# %%
## Group ages into bins.
df_baseline['age'] = df_baseline['age'].astype(int)

bins = [1, 5, 11, 14, 16, 18]
labels = ['<5', '5-11', '12-14', '14-16', '17-18']

df_baseline['age'] = pd.cut(df_baseline['age'], bins=bins, labels=labels)

# %%
## Map job/occupation column.
occup_dict = {
'1':'Farmer',
'2':'Fishing/Fishmonger',
'3':'Shopkeeper/Market vendor',
'4':'Bar owner/Bar worker',
'5':'Transport [truck, taxi, motorcycle, bike, boat] drivers',
'6':'Hotel/Restaurant worker',
'7':'Tourism',
'8':'Teacher',
'9':'Student',
'10':'Government worker',
'11':'Military',
'12':'Housewife',
'13':'Household worker',
'14':'Healthcare worker',
'15':'Construction worker',
'16':'Factory worker',
'17':'Mining',
'18':'Disabled',
'19':'No job',
'20':'Other',
}
df_baseline['occup'] = df_baseline['occup'].map(occup_dict)

# %%
## Map marital column.
marital_dict = {
    '1':'Single',
    '2':'Married',
    '3':'Widowed',
    '4':'Divorced',
    '5':'Separated',
}
df_baseline['marital'] = df_baseline['marital'].map(marital_dict)

# %%
## Map sex column.
df_baseline['sex'] = df_baseline['sex'].map({'1':'Male', '2':'Female'})

# %%
## Map education column.
education_dict = {
'0':'No school',
'1':'P1-P6',
'2':'P7',
'3':'S1-S3',
'4':'S4',
'5':'S5',
'6':'S6',
'7':'Tertiary/Vocational',
'8':'University',
'9':'Post-graduate',
'10':'Pre-primary',
}
df_baseline['education'] = df_baseline['education'].map(education_dict)


# %%
# Define Components

## Screening

### Screened/Consented cards
def create_card(title, data) -> dbc.Card:
    return dbc.Card([dbc.CardHeader(title),
                     dbc.CardBody(html.H3(data))],
                     color='primary')

# %%
card_titles = ['# of Screened Overall','# Screened & Consented',"% Screened & Consented"]
card_data = [num_screened, num_consent, percent_consent]

# %%
screening_cards = [create_card(title, data) for title, data in zip(card_titles, card_data)]

# %%
### Graphs

#### Screened over time
over_time_fig = px.line(x=df_baseline_date['starttime'],
                        y=df_baseline_date['one'].cumsum(),
                        labels={'vdate':'Date', 'y':'Total Screened'},
                        title="Total Screened Over Time")
over_time_graph = dcc.Graph(figure=over_time_fig)

#### Screened by interviewer
by_int_fig = px.histogram(x=df_baseline.value_counts('ranum').index,
                   y=df_baseline.value_counts('ranum').values,
                   labels={'x':'RA ID', 'y':'participants screened'},
                   title="Number of participants screened per interviewer")
# update xaxes to categorical type so that each ID appears on the graph
by_int_fig.update_xaxes(type='category')
by_int_graph = dcc.Graph(figure=by_int_fig)

# %%
### Consort Diagram
# Chart object.
consort_chart = f"""
flowchart TB
    0(Enrollment)
    1["Assessed for Eligibility (n={num_screened})"]
    p1[ ]
    2["Randomized (n= )"]
    3["Excluded (n={num_no_consent}) <br> • Not meeting inclusion criteria (n= ) <br> • Declined to participate (n={num_no_consent}) <br> • Other reason (n= )"]
    p2[ ]
    4(Allocation)
    5["Allocated to intervention (n= )"]
    6["Allocated to control (n= )"]
    
    1 --- p1
    p1 --> 2
    p1 --> 3
    2 --> p2
    p2 --> 5
    p2 --- 4
    p2 --> 6

    linkStyle 5 stroke-width:0px
    style 3 text-align:left
    style p1 width:0px
    style p2 width:0px
"""

# %%
### TableOne table
t1_cols = ['age','sex','marital','occup','education']
t1 = TableOne(df_baseline, columns=t1_cols)
df_t1 = t1.tableone.reset_index()
df_t1.columns = [' ', ' ', 'Missing', 'Overall']

# %%
# App Layout

## Style arguments
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "12rem",
    "padding": "1rem 1rem",
    "background-color": "#f8f9fa"
}

# Content position to the right, padding.
CONTENT_STYLE = {
   "margin-left": "13rem",
   "margin-right": "0rem",
   "margin-down": "13rem",
   "padding": "2rem 1rem" 
}

# Navbar position to the right, padding.
NAVBAR_STYLE = {
   "margin-left": "12rem",
   "margin-right": "0rem"
}

# %%
## Sidebar object
sidebar = html.Div(
    [ 
     #html.H2("SONET Dashboard", className="display-5"),
     html.Hr(),
     html.P(
         "SONET Dashboard", className="lead"
     ),
     dbc.Nav(
         [ 
            dbc.NavLink("Screening", href="/", active="exact"),
            dbc.NavLink("Enrollment", href="/page-1", active="exact"),
            dbc.NavLink("Consort", href="/page-2", active="exact"),
            dbc.NavLink("Table One", href="/page-3", active="exact"),
            dbc.NavLink("Qualitative Data", href="/page-4", active="exact")],
            vertical=True,
            pills=True
            ),
     ],
    style=SIDEBAR_STYLE
)

# %%
## Navbar object
navbar = dbc.NavbarSimple(
    children=[html.Img(src="https://static.wixstatic.com/media/06913a_2a6641f3d15f4c2997954aea3366b05b.png/v1/fill/w_439,h_252,al_c,q_85,usm_0.66_1.00_0.01/06913a_2a6641f3d15f4c2997954aea3366b05b.webp",
                       width='15%',
                       height='15%')],
    fluid=True,
    style=NAVBAR_STYLE
)

# %%
## Content object
content = html.Div(id="page-content", style=CONTENT_STYLE)

# %%
## Screening dashboard container
screening_dash_container = dbc.Container(
    [
        html.H1("Screening Dashboard"),
        html.Hr(),
        dbc.Row([dbc.Col(card) for card in screening_cards]),
        html.Br(),
        dbc.Row([dbc.Col(over_time_graph), dbc.Col(by_int_graph)])
    ]
)

# %%
## Consort dashboard container
consort_dash_container = dbc.Container(
    [
        html.H1("Consort Dashboard"),
        html.Hr(),
        html.Div(Mermaid(chart=consort_chart))
    ]
)

# %%
## TableOne dashboard container
t1_dash_container = dbc.Container(
    [
        html.H1("Table One Dashboard"),
        html.Hr(),
        dbc.Table.from_dataframe(df_t1, striped=True, bordered=True, hover=True)
    ]
)

# %%
## Init app
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# %%
## App layout.
app.layout = html.Div([dcc.Location(id="url"), navbar, sidebar, content])

# %%
# App callback setup, render page.
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return screening_dash_container
    elif pathname == "/page-1":
        return html.P("Enrollment Coming Soon!")
    elif pathname == "/page-2":
        return consort_dash_container
    elif pathname == "/page-3":
        return t1_dash_container
    elif pathname == "/page-4":
        return html.P("Qualitative Data Coming Soon!")
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )

# %%
if __name__ == "__main__":
    app.run_server(debug=True, port='8880')