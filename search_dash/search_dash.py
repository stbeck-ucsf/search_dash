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
from mcr_toolkit.dataset_tools import gen_baseline_dataset, fetch_df, gen_tx_tableone

# %%
# Data Manipulation

## Fetch data
df_enrollment = fetch_df('mobility', 'enrollment')
df_screening = fetch_df('mobility', 'screening')
df_baseline = gen_baseline_dataset('mobility')

# %%
df_baseline

# %%
## Get total number screened.
num_screened = df_screening['subjid'].unique().shape[0]

# %%
## Get total number who consented.
num_consent = df_screening[df_screening['obtainedconsent'] == 'Yes'].shape[0]

# %%
## Get the number who actively declined consent.
num_no_consent = df_screening[df_screening['obtainedconsent'] != 'Yes'].shape[0]

# %%
## Get percentage screened who have consented.
percent_consent = "{:.0%}".format(num_consent/num_screened)

# %%
df_screening_date = df_screening.sort_values(by='starttime')

# %%
df_screening_date['one'] = 1

# %%
# Enrollment numbers

## Study Arm
intervention = df_enrollment[df_enrollment['studyarm'] == 'Intervention']
control = df_enrollment[df_enrollment['studyarm'] == 'Control']

num_intervention = intervention.shape[0]
num_control = control.shape[0]

# %%
## Total enrolled
num_enrolled = df_enrollment['subjid'].unique().shape[0]

# %%
## Enrollment over time
df_enrollment_date = df_enrollment.sort_values(by='starttime')
df_enrollment_date['one'] = 1

# %%
## Enrollment qualification numbers
# Create sub-data-sets based on eligibility criteria filters.

## Ineligible due to age.
df_age_filter = df_screening[df_screening['age'] == 'Yes']
num_disqual_age = df_screening['subjid'].unique().shape[0] - df_age_filter.shape[0]

## Ineligible due to HIV status.
df_hiv_filter = df_age_filter[df_age_filter['hivstatus'] == 'Yes']
num_disqual_hiv = df_age_filter.shape[0] - df_hiv_filter.shape[0]

## Ineligible due to Viral Load, Visits, or Care Status.
df_vl_vst_enr_filter = df_age_filter[((df_age_filter['rna'] == 'Yes') | (df_age_filter['novl'] == 'Yes')) | (df_age_filter['mvisits'] == 'Yes') | (df_age_filter['enrolled'] == 'Yes')]
num_disqual_vl = df_hiv_filter.shape[0] - df_vl_vst_enr_filter.shape[0]

## Ineligible due to Travel.
df_travel_filter = df_vl_vst_enr_filter[(df_vl_vst_enr_filter['travel'] == 'Yes') | (df_vl_vst_enr_filter['travel_cum'] == 'Yes')]
num_disqual_travel = df_vl_vst_enr_filter.shape[0] - df_travel_filter.shape[0]

## Ineligible due to enrollment in RCT.
df_rct_filter = df_travel_filter[(df_travel_filter['in_other_rct'].isna()) | (df_travel_filter['in_other_rct'] == 'No')]
num_disqual_rct = df_travel_filter.shape[0] - df_rct_filter.shape[0]

## Total ineligible
num_disqual_total = num_disqual_age + num_disqual_hiv + num_disqual_travel + num_disqual_vl + num_disqual_rct

# %%
## Percentage enrolled of screened
percent_enrolled_screen = "{:.0%}".format(num_enrolled/num_screened)

## Percentage enrolled of eligible
percent_enrolled_eligible = "{:.0%}".format(num_enrolled/df_rct_filter.shape[0])

# %%
## Exclusion reasons DataFrame
df_exclusion = pd.DataFrame({
    "exclusion_reason":
        ["Did not consent",
        "Ineligible due to age",
        "Ineligible due to HIV status",
        "Ineligible due to Viral Load",
        "Ineligible due to lack of travel",
        "Ineligible due to enrollment in other RCT"
        ],
    "number":
        [
            num_no_consent,
            num_disqual_age,
            num_disqual_hiv,
            num_disqual_vl,
            num_disqual_travel,
            num_disqual_rct
        ]
})
# %%
## Total excluded
num_excluded_total = num_disqual_total + num_no_consent

# %%
# Define Components

## Screening

### Screened/Consented cards
def create_card(title, data, color='primary') -> dbc.Card:
    return dbc.Card([dbc.CardHeader(title),
                     dbc.CardBody(html.H3(data))],
                     color=color)

# %%
### Define cards
# Data Quality
qual_card_titles = ["Baseline Dataset Testing", "Baseline Dataset Validation", "Baseline Dataset Locked", "Baseline Dataset Generated"]
qual_card_data = ["In Progress", "Done", "In Progress", "Not Started"]


# Screening
screening_card_titles = ['# of Screened Overall','# Screened & Consented',"% Screened & Consented"]
screening_card_data = [num_screened, num_consent, percent_consent]

# Enrollment
enrollment_card_titles = ["# Enrolled", "% of Screened Enrolled", "% of Eligible Enrolled"]
enrollment_card_data = [num_enrolled, percent_enrolled_screen, percent_enrolled_eligible]

# %%
# Data Quality Cards
qual_cards = []
for title, data in zip(qual_card_titles, qual_card_data):
    if data == "Not Started":
        color = 'danger'
    elif data == "In Progress":
        color = 'warning'
    elif data == "Done":
        color = 'success'
    card = create_card(title, data, color=color) 
    qual_cards.append(card)


# Screening Cards
screening_cards = [create_card(title, data) for title, data in zip(screening_card_titles, screening_card_data)]

# %%
# Enrollment Cards
enrollment_cards = [create_card(title, data) for title, data in zip(enrollment_card_titles, enrollment_card_data)]

# %%
### Graphs

#### Screened over time
screen_over_time_fig = px.line(x=df_screening_date['starttime'],
                        y=df_screening_date['one'].cumsum(),
                        labels={'vdate':'Date', 'x':'Date', 'y':'Total Screened'},
                        title="Total Screened Over Time")
screen_over_time_graph = dcc.Graph(figure=screen_over_time_fig)

#### Enrolled over time
enroll_over_time_fig = px.line(x=df_enrollment_date['starttime'],
                        y=df_enrollment_date['one'].cumsum(),
                        labels={'vdate':'Date', 'x':'Date', 'y':'Total Enrolled'},
                        title="Total Enrolled Over Time")
enroll_over_time_graph = dcc.Graph(figure=enroll_over_time_fig)

#### Screened by interviewer
by_int_fig = px.histogram(x=df_baseline.value_counts('intvinit').index,
                   y=df_baseline.value_counts('intvinit').values,
                   labels={'x':'Interviewer ID', 'y':'participants screened'},
                   title="Number of participants screened per interviewer")
# update xaxes to categorical type so that each ID appears on the graph
by_int_fig.update_xaxes(type='category')
by_int_graph = dcc.Graph(figure=by_int_fig)

#### Enrollment study arm bar chart
enroll_study_arm_fig = px.bar(x=['Control', 'Intervention'],
                              y=[num_control, num_intervention],
                              labels={'x':'Study Arm', 'y':'Number enrolled'},
                              title='Enrollment by Study Arm')
enroll_study_arm_graph = dcc.Graph(figure=enroll_study_arm_fig)

#### Enrollment exclusion tree map
enroll_exclusion_fig = px.treemap(df_exclusion,
                                  path=['exclusion_reason'],
                                  values='number',
                                  title="Exclusion Reasons")
enroll_exclusion_graph = dcc.Graph(figure=enroll_exclusion_fig)

# %%
### Consort Diagram
# Chart object.
consort_chart = f"""
flowchart TB
    0(Enrollment)
    1["Assessed for Eligibility (n={num_screened})"]
    p1[ ]
    2["Randomized (n={num_enrolled})"]
    3["Excluded (n={num_excluded_total})
        • Not meeting inclusion criteria (n={num_disqual_total})
            • Ineligible due to age (n={num_disqual_age})
            • Ineligible due to HIV status (n={num_disqual_hiv})
            • Ineligible due to viral load, visits, or care status (n={num_disqual_vl})
            • Ineligible due to lack of travel (n={num_disqual_travel})
            • Ineligible due to enrollment in other RCT (n={num_disqual_rct})
        • Declined to participate (n={num_no_consent})
        • Other reason (n=0)
        "]
    p2[ ]
    4(Allocation)
    5["Allocated to intervention (n={num_intervention})"]
    6["Allocated to control (n={num_control})"]
    
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
t1 = gen_tx_tableone(df_baseline, 'mobility', format=None)
df_t1 = t1.tableone.reset_index()
df_t1.columns = [' ', ' ', 'Missing', 'Overall', 'Control', 'Intervention']

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
     html.Img(src="https://static.wixstatic.com/media/06913a_2a6641f3d15f4c2997954aea3366b05b.png/v1/fill/w_439,h_252,al_c,q_85,usm_0.66_1.00_0.01/06913a_2a6641f3d15f4c2997954aea3366b05b.webp",
              height="15%",
              width="100%"),
     html.Hr(),
     html.P(
         "SAPPHIRE Dashboard", className="lead"
     ),
     dbc.Nav(
         [ 
            dbc.NavLink("Data Overview", href="/", active="exact"),
            dbc.NavLink("Screening", href="/page-1", active="exact"),
            dbc.NavLink("Enrollment", href="/page-2", active="exact"),
            dbc.NavLink("Consort", href="/page-3", active="exact"),
            dbc.NavLink("Table One", href="/page-4", active="exact"),
            dbc.NavLink("Qualitative Data", href="/page-5", active="exact")],
            vertical=True,
            pills=True
            ),
     ],
    style=SIDEBAR_STYLE
)

# %%
## Navbar object
navbar = dbc.NavbarSimple(
        [dbc.DropdownMenu(
            label="Study Name",
            children=[
                dbc.DropdownMenuItem("Mobility", id="mobility"),
                dbc.DropdownMenuItem("Alcohol", id="alcohol"),
                dbc.DropdownMenuItem("Hypertension", id="htn")],
            in_navbar=True,
            id="study-name")
              ],
    fluid=True,
    style=NAVBAR_STYLE
)

# %%
## Content object
content = html.Div(id="page-content", style=CONTENT_STYLE)

# %%
## Data Quality dashboard container
qual_dash_container = dbc.Container(
    [
        html.H1("Dataset Progress Overview"),
        html.Hr(),
        dbc.Row([dbc.Col(card) for card in qual_cards])
    ]
)


## Screening dashboard container
screening_dash_container = dbc.Container(
    [
        html.H1("Screening Dashboard"),
        html.Hr(),
        dbc.Row([dbc.Col(card) for card in screening_cards]),
        html.Br(),
        dbc.Row([dbc.Col(screen_over_time_graph), dbc.Col(by_int_graph)])
    ]
)

# %%
## Enrollment dashboard container
enrollment_dash_container = dbc.Container(
    [ 
        html.H1("Enrollment Dashboard"),
        html.Hr(),
        dbc.Row([dbc.Col(card) for card in enrollment_cards]),
        html.Br(),
        dbc.Row([dbc.Col(enroll_study_arm_graph), dbc.Col(enroll_exclusion_graph)]),
        html.Br(),
        dbc.Row([dbc.Col(enroll_over_time_graph)])
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
# App callback filter, setup, render page.
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return qual_dash_container
    elif pathname == "/page-1":
        return screening_dash_container
    elif pathname == "/page-2":
        return enrollment_dash_container
    elif pathname == "/page-3":
        return consort_dash_container
    elif pathname == "/page-4":
        return t1_dash_container
    elif pathname == "/page-5":
        return html.P("Qualitative Data Coming Soon!")
    # If the user tries to reach a different page, return a 404 message
    dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )

# %%
if __name__ == "__main__":
    app.run_server(debug=True, port='8880')
