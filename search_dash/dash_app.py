import dash_auth
import dash_bootstrap_components as dbc
import pandas as pd
from dash import Dash, Input, Output, dcc, html
from dash_consort import consort_script
from dash_extensions import Mermaid

## Style arguments.
# Style arguments.
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa"
}

# Content position to the right, padding.
CONTENT_STYLE = {
   "margin-left": "18rem",
   "margin-right": "2rem",
   "margin-down": "18rem",
   "padding": "2rem 1rem" 
}

# Navbar position to the right, padding.
NAVBAR_STYLE = {
   "margin-left": "12rem",
   "margin-right": "2rem"
}

# Auth password pairs (for testing only).
VALID_USERNAME_PASSWORD_PAIRS = {
    'green':'day'
}

## App objects.
# Sidebar object.
sidebar = html.Div(
    [ 
     html.H2("Dashboard", className="display-5"),
     html.Hr(),
     html.P(
         "A simple sidebar layout with navigation links", className="lead"
     ),
     dbc.Nav(
         [ 
          dbc.NavLink("Home", href="/", active="exact"),
          dbc.NavLink("Consort", href="/page-1", active="exact"),
          dbc.NavLink("Page 2", href="/page-2", active="exact")],
         vertical=True,
         pills=True
            ),
     ],
    style=SIDEBAR_STYLE
)

# Navbar object.
navbar = dbc.NavbarSimple(
    children=[html.Img(src="https://static.wixstatic.com/media/06913a_2a6641f3d15f4c2997954aea3366b05b.png/v1/fill/w_439,h_252,al_c,q_85,usm_0.66_1.00_0.01/06913a_2a6641f3d15f4c2997954aea3366b05b.webp",
                       width='15%',
                       height='15%')],
    fluid=True,
    style=NAVBAR_STYLE
)

# Content object.
content = html.Div(id="page-content", style=CONTENT_STYLE)

## App object w/ authentication.
app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)

## App layout.
app.layout = html.Div([dcc.Location(id="url"), navbar, sidebar, content])

## App callback setup, render page.
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return html.P("SEARCH Dashboard Home")
    elif pathname == "/page-1":
        return html.Div(Mermaid(chart=consort_script))
    elif pathname == "/page-2":
        return html.P("Oh cool, this is page 2!")
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )

if __name__=="__main__":
    app.run_server(debug=True)