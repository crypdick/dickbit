"""
tutor display 10 fingers
self ""
python fetch keys
decide on mapping from 10-fingers to letters
"""


import dash
import dash_daq as daq
import dash_html_components as html
import keyboard



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    daq.Indicator(
        id='my-indicator',
        label="L5",
    ),
    daq.Indicator(
        id='my-indicator',
        label="L4",
    ),
    daq.Indicator(
        id='my-indicator',
        label="L3",
    ),
    daq.Indicator(
        id='my-indicator',
        label="L2",
    ),
    daq.Indicator(
        id='my-indicator',
        label="L1",
    )
])


@app.callback(
    dash.dependencies.Output('my-indicator', 'value'),
    [dash.dependencies.Input('my-indicator-button', 'n_clicks')]
)
def update_output(value):
    if value % 2 is 0:
        value = True
    else:
        value = False
    return value


if __name__ == '__main__':
    app.run_server(debug=True)