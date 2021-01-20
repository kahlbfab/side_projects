import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime
from datetime import timedelta
import plotly.graph_objects as go


def conv_to_datetime(col_minutes, col_seconds):
    return pd.to_datetime(col_minutes * 60 + col_seconds, unit='s')


def highlight_goal_achieved(s):
    if s.Ziel_Erreicht:
        return ['background-color: mediumseagreen']*len(s)
    else:
            return ''


def convert_min_s(x):
    min_s = divmod(x.total_seconds(), 60)
    return "{}min {}s".format(min_s[0], min_s[1])

def preprocess(df):

    df['Name'] = df['Vorname'] + ' ' + df['Nachname'] 

    df['goal_time'] = conv_to_datetime(df['goal_min'], df["goal_s"])
    df['eff_time'] = conv_to_datetime(df['eff_min'], df["eff_s"])


    df['goal_achieved'] = df['eff_time'] >= df['goal_time']
    df['goal_diff'] = df['eff_time'] - df['goal_time']
    df['goal_diff'] = df['goal_diff'].apply(convert_min_s)

    df.sort_values(by=['eff_time'], ascending=False, inplace=True)
    df['Rank'] = np.arange(start=1, stop=df.shape[0] + 1, step=1) 
    df.set_index('Rank', inplace=True)

    # drop unnecessary attributes
    df.drop(['goal_min',
             'goal_s',
             'eff_min',
             'eff_s',
             'Vorname',
             'Nachname'],
             axis=1, inplace=True)

    # rearrange colums
    df = df[['Name', 'eff_time', 'goal_time', 'goal_diff', 'goal_achieved']]
    
    return df

def create_nice_styler(df):
    df_nice = df.rename(
        columns=
            {
                'goal_time': 'Ziel_Zeit',
                'eff_time': 'Effektive_Zeit',
                'goal_achieved': 'Ziel_Erreicht',
                'goal_diff': 'Differenz'
            })

    df_nice = df_nice.style.apply(highlight_goal_achieved, axis=1)

    df_nice.format(
    {
        "Ziel_Zeit": lambda x: x.strftime("%Mmin %Ss"),
        "Effektive_Zeit": lambda x: x.strftime("%Mmin %Ss"),
    })

    return df_nice

# load data
df_plank = pd.read_csv("plank_time.csv", header=[0])
df_plank = preprocess(df_plank)
df_plank_nice = create_nice_styler(df_plank)

## streamlit
st.title('Plank Challene 2021')

st.write("# Resultate")
st.write(df_plank_nice)

## plot
fig = go.Figure([

        go.Scatter(
            x=df_plank['Name'],
            y=df_plank['eff_time'],
            mode='markers',
            name = 'Effektive Zeit',
            #marker_color=data['Population'],
            #text=df_plank['goal_diff'] # hover text goes here
        ),
        go.Scatter(
            x=df_plank['Name'],
            y=df_plank['goal_time'],
            mode='markers',
            name = 'Ziel Zeit',
        )
])

fig.update_layout(title='Ziel Zeit -> Effektive Zeit')
fig.update_yaxes(title_text='Zeit')
fig.update_yaxes(tickformat="%Mmin %Ss")

st.plotly_chart(fig)