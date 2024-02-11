import dash
from dash import dcc
from dash import html
from dash.dependencies import Output, Input
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import math
import numpy as np
from os import chdir,getcwd,listdir,makedirs
from os.path import dirname,abspath,join,isdir,isfile

def get_work_dir():
    chdir(dirname(abspath(__file__)))
    return getcwd()

def my_floor(a, precision=0):
    return np.true_divide(np.floor(a * 10**precision), 10**precision)
def my_ceil(a, precision=0):
    return np.round(a + 0.5 * 10**(-precision), precision)

def my_ceil_2(a):
    return math.log10(my_ceil(a,int(my_ceil(abs(math.log10(a))))))
def my_floor_2(a):
    return math.log10(my_floor(a,int(my_ceil(abs(math.log10(a))))))

# Read the data from out.csv file and store it in a pandas dataframe
df = pd.read_csv(join(get_work_dir(),'out_files','Normalized','out_2024_01_25_14_17_09.csv'))

df=df[df['k_Value']!=0]

df['Norm_Density']=2300*df['Norm_Density']

df=df[df["k_Value"]!=0]

# Create the dash app
app = dash.Dash()
app.layout = html.Div([
    # Add a horizontal container for the dropdown menus
    
    html.Div(
        style={"display": "flex", "justify-content": "space-between"},
        children=[html.Div('Legend Color Category:',style={"text-align": "right", "width": "100%", "padding-right": "10px"}),
                dcc.RadioItems(
                    [{"label": 'k Value .', "value": 'k_Value'},{"label": 'Hybrid Percentage .', "value": 'Hybrid_Perc'},{"label": 'Length', "value": 'length'}],
                    'k_Value',
                    id='legend_category',
                    inline=False,
                    style={"display": "flex","text-align": "left", "width": "100%"})]),

    
    html.Div(
        style={"display": "flex", "justify-content": "space-between"},
        children=[
            dcc.Dropdown(
                id="geom1-dropdown",
                options=[{"label": 'Select geom-1 here', "value": "All"}]+[{"label": x, "value": x} for x in df["Geom1"].unique()],
                value="All",
                placeholder='Select geom-1 here',
                clearable=False,
                style={"width": "90%"}
            ),
            dcc.Dropdown(
                id="geom2-dropdown",
                options=[{"label": 'Select geom-2 here', "value": "All"}]+[{"label": x, "value": x} for x in df["Geom2"].unique()],
                value="All",
                placeholder='Select geom-2 here',
                clearable=False,
                style={"width": "90%"}
            ),
            dcc.Dropdown(
                id="k-value-dropdown",
                options=[{"label": 'Select k-value here', "value": "All"}]+[{"label": x, "value": x} for x in df["k_Value"].unique()],
                value="All",
                placeholder='Select k-value here',
                clearable=False,
                style={"width": "90%"}
            ),
            dcc.Dropdown(
                id="hybrid-perc-dropdown",
                options=[{"label": 'Select %hybrid here', "value": "All"}]+[{"label": x, "value": x} for x in df["Hybrid_Perc"].unique()],
                value="All",
                placeholder='Select %hybrid here',
                clearable=False,
                style={"width": "90%"}
            ),
            dcc.Dropdown(
                id="length-dropdown",
                options=[{"label": 'Select length here', "value": "All"}]+[{"label": x, "value": x} for x in df["length"].unique()],
                value="All",
                placeholder='Select length here',
                clearable=False,
                style={"width": "90%"}
            ),
        ]
    ),
    html.Div(
        style={"display": "flex","justify-content": "space-between"},
        children=[
            dcc.Graph(id="norm-stress-norm-density-scatter"),
            dcc.Graph(id="norm-young-modulus-norm-density-scatter")

            ]),
    html.Div(
        style={"display": "flex","justify-content": "space-between", "width":"100%"},
        children=[
            dcc.Graph(id="stress-strain-scatter_1"),
            dcc.Graph(id="stress-strain-scatter_2")
            ]),
    html.Div(
        style={"display": "flex","justify-content": "space-between", "width":"100%"},
        children=[
            dcc.Graph(id="stress-strain-scatter_3"),
            dcc.Graph(id="stress-strain-scatter_4")
            ]),
        html.Div(
        style={"display": "flex","justify-content": "space-between", "width":"100%"},
        children=[
            dcc.Graph(id="energy-scatter_1"),
            dcc.Graph(id="energy-scatter_2")
            ])
])

# Define a callback function to update the plots based on the selected filters
@app.callback(
    [
        Output("norm-stress-norm-density-scatter", "figure"),
        Output("norm-young-modulus-norm-density-scatter", "figure"),
        Output("stress-strain-scatter_1", "figure"),
        Output("stress-strain-scatter_2", "figure"),
        Output("stress-strain-scatter_3", "figure"),
        Output("stress-strain-scatter_4", "figure"),
        Output("energy-scatter_1", "figure"),
        Output("energy-scatter_2", "figure")
    ],
    [
        Input("geom1-dropdown", "value"),
        Input("geom2-dropdown", "value"),
        Input("k-value-dropdown", "value"),
        Input("hybrid-perc-dropdown", "value"),
        Input("length-dropdown", "value"),
        Input("legend_category","value")
    ]
)
def update_plots(geom1, geom2, k_value, hybrid_perc,length,legend_Category):
    # Filter the data based on the selected values
    df_filtered = df

    colorMin=math.floor(min(df_filtered[legend_Category]))
    colorMax=round(min(df_filtered[legend_Category]))
    

    if geom1 != "All":
        df_filtered = df_filtered[df_filtered["Geom1"] == geom1]
    if geom2 != "All":
        df_filtered = df_filtered[df_filtered["Geom2"] == geom2]
    if k_value != "All":
        df_filtered = df_filtered[df_filtered["k_Value"] == k_value]
    if hybrid_perc != "All":
        df_filtered = df_filtered[df_filtered["Hybrid_Perc"] == hybrid_perc]
    if length != "All":
        df_filtered = df_filtered[df_filtered["length"] == length]

    df_filtered['normstress_wMass']=df_filtered['Max_Stress']/df_filtered['TotalAtom']
    df_filtered['normstress_wDens']=df_filtered['Max_Stress']/df_filtered['Norm_Density']

    # Create the scatter plots with the filtered data
    figure1 = px.scatter(df_filtered,labels={"k_Value": "k Value", "length": "Length<br> ", "Hybrid_Perc":"Hybrid<br>Percentage<br>"}, x="Norm_Density", y="Max_Stress",hover_data=["Geom1", "Geom2","length", "k_Value", "Hybrid_Perc"],color=legend_Category,trendline='ols',trendline_options=dict(log_x=True,log_y=True),height=750)
    figure2 = px.scatter(df_filtered,labels={"k_Value": "k Value", "length": "Length<br> ", "Hybrid_Perc":"Hybrid<br>Percentage<br>"}, x="Norm_Density", y="Young_Modulus",hover_data=["Geom1", "Geom2","length", "k_Value", "Hybrid_Perc"],color=legend_Category,trendline='ols',trendline_options=dict(log_x=True,log_y=True))
    figure3 = px.scatter(df_filtered,labels={"k_Value": "k Value", "length": "Length<br> ", "Hybrid_Perc":"Hybrid<br>Percentage<br>"}, x="Norm_Density", y="norm_stress_geom1",hover_data=["Geom1", "Geom2","length", "k_Value", "Hybrid_Perc"],color=legend_Category,trendline='ols',trendline_options=dict(log_x=True,log_y=True),height=750)
    figure4 = px.scatter(df_filtered,labels={"k_Value": "k Value", "length": "Length<br> ", "Hybrid_Perc":"Hybrid<br>Percentage<br>"}, x="Norm_Density", y="norm_stress_geom2",hover_data=["Geom1", "Geom2","length", "k_Value", "Hybrid_Perc"],color=legend_Category,trendline='ols',trendline_options=dict(log_x=True,log_y=True),height=750)
    figure5 = px.scatter(df_filtered,labels={"k_Value": "k Value", "length": "Length<br> ", "Hybrid_Perc":"Hybrid<br>Percentage<br>"}, x="Norm_Density", y="norm_young_geom1",hover_data=["Geom1", "Geom2","length", "k_Value", "Hybrid_Perc"],color=legend_Category,trendline='ols',trendline_options=dict(log_x=True,log_y=True),height=750)
    figure6 = px.scatter(df_filtered,labels={"k_Value": "k Value", "length": "Length<br> ", "Hybrid_Perc":"Hybrid<br>Percentage<br>"}, x="Norm_Density", y="norm_young_geom2",hover_data=["Geom1", "Geom2","length", "k_Value", "Hybrid_Perc"],color=legend_Category,trendline='ols',trendline_options=dict(log_x=True,log_y=True),height=750)
    figure7 = px.scatter(df_filtered,labels={"k_Value": "k Value", "length": "Length<br> ", "Hybrid_Perc":"Hybrid<br>Percentage<br>"}, x="Norm_Density", y="norm_young_geom1",hover_data=["Geom1", "Geom2","length", "k_Value", "Hybrid_Perc"],color=legend_Category,trendline='ols',trendline_options=dict(log_x=True,log_y=True),height=750)
    figure8 = px.scatter(df_filtered,labels={"k_Value": "k Value", "length": "Length<br> ", "Hybrid_Perc":"Hybrid<br>Percentage<br>"}, x="Norm_Density", y="norm_young_geom2",hover_data=["Geom1", "Geom2","length", "k_Value", "Hybrid_Perc"],color=legend_Category,trendline='ols',trendline_options=dict(log_x=True,log_y=True),height=750)


    figArr=[figure1,figure2,figure3,figure4,figure5,figure6]
    
    for figR in figArr[2::]:
        figR.add_shape(
            type='rect',
            y0=1,
            x0=0,
            y1=2,
            x1=1500,opacity=0.2,fillcolor='lightgreen',showlegend=False
        )


    fig1YMin=min(df["Max_Stress"])*0.9
    fig1YMax=max(df["Max_Stress"])*1.1

    fig1XMin=min(df["Norm_Density"])*0.9
    fig1XMax=max(df["Norm_Density"])*1.1

    figure1.update_layout(xaxis=dict(range=[my_floor_2(fig1XMin),my_ceil_2(fig1XMax)],type='log'))
    figure1.update_layout(yaxis=dict(range=[my_floor_2(fig1YMin),my_ceil_2(fig1YMax)],type='log'))
    figure1.update_layout(coloraxis=dict(cmin=colorMin, cmax=colorMax))

    fig2YMin=min(df["Young_Modulus"])*0.9
    fig2YMax=max(df["Young_Modulus"])*1.1

    fig2XMin=min(df["Norm_Density"])*0.9
    fig2XMax=max(df["Norm_Density"])*1.1

    figure2.update_layout(xaxis=dict(range=[my_floor_2(fig2XMin),my_ceil_2(fig2XMax)],type='log'))
    figure2.update_layout(yaxis=dict(range=[my_floor_2(fig2YMin),my_ceil_2(fig2YMax)],type='log'))
    figure2.update_layout(coloraxis=dict(cmin=colorMin, cmax=colorMax))
    
    figure3.update_layout(xaxis=dict(range=[my_floor_2(fig2XMin),my_ceil_2(fig2XMax)],type='log'))
    figure3.update_layout(yaxis=dict(range=[my_floor_2(min(df["norm_stress_geom1"])),my_ceil_2(1.45)],type='log'))
    figure3.update_layout(coloraxis=dict(cmin=colorMin, cmax=colorMax))
    
    figure4.update_layout(xaxis=dict(range=[my_floor_2(fig2XMin),my_ceil_2(fig2XMax)],type='log'))
    figure4.update_layout(yaxis=dict(range=[my_floor_2(min(df["norm_stress_geom2"])),my_ceil_2(1.45)],type='log'))
    figure4.update_layout(coloraxis=dict(cmin=colorMin, cmax=colorMax))
    
    figure5.update_layout(xaxis=dict(range=[my_floor_2(fig2XMin),my_ceil_2(fig2XMax)],type='log'))
    figure5.update_layout(yaxis=dict(range=[my_floor_2(min(df["norm_young_geom2"])),my_ceil_2(2)],type='log'))
    figure5.update_layout(coloraxis=dict(cmin=colorMin, cmax=colorMax))
    
    figure6.update_layout(xaxis=dict(range=[my_floor_2(fig2XMin),my_ceil_2(fig2XMax)],type='log'))
    figure6.update_layout(yaxis=dict(range=[my_floor_2(min(df["norm_young_geom2"])),my_ceil_2(2)],type='log'))
    figure6.update_layout(coloraxis=dict(cmin=colorMin, cmax=colorMax))

    font_size=20
    for figAxes in figArr:
        figAxes.update_xaxes(showline=True, mirror=True, gridcolor='lightgrey')
        figAxes.update_yaxes(showline=True, mirror=True ,gridcolor='lightgrey')
        figAxes.update_layout(font=dict(family= "Times New Roman",size=font_size),template='none')

    
    figure1.update_layout(xaxis_title="Density[mg/cm<sup>3</sup>]", yaxis_title="Yield Strength [GPa]")
    figure2.update_layout(xaxis_title="Density[mg/cm<sup>3</sup>]", yaxis_title="Young Modulus [GPa]")
    figure3.update_layout(xaxis_title="Density[mg/cm<sup>3</sup>]", yaxis_title="Normalized Yield Strength via Type-1")
    figure4.update_layout(xaxis_title="Density[mg/cm<sup>3</sup>]", yaxis_title="Normalized Yield Strength via Type-2")
    figure5.update_layout(xaxis_title="Density[mg/cm<sup>3</sup>]", yaxis_title="Normalized Young Modulus via Type-1")
    figure6.update_layout(xaxis_title="Density[mg/cm<sup>3</sup>]", yaxis_title="Normalized Young Modulus via Type-2") 
    

    return figure1, figure2, figure3, figure4, figure5, figure6, figure7, figure8


if __name__ == '__main__':
    app.run_server( host="127.0.0.1", port="5500", debug=False, dev_tools_ui=False, dev_tools_props_check=False)
