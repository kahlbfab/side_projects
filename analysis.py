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


df_plank = pd.read_csv("plank_time.csv", header=[0])

df_plank['Name'] = df_plank['Vorname'] + ' ' + df_plank['Nachname'] 

df_plank['goal_time'] = conv_to_datetime(df_plank['goal_min'], df_plank["goal_s"])
df_plank['eff_time'] = conv_to_datetime(df_plank['eff_min'], df_plank["eff_s"])

# goal achieved
df_plank['goal_achieved'] = df_plank['eff_time'] >= df_plank['goal_time']

df_plank['goal_diff'] = df_plank['eff_time'] - df_plank['goal_time']
df_plank['goal_diff'] = df_plank['goal_diff'].apply(convert_min_s)

df_plank.drop(['goal_min',
               'goal_s',
               'eff_min',
               'eff_s',
               'Vorname',
               'Nachname'],
               axis=1, inplace=True)

df_plank.sort_values(by=['eff_time'], ascending=False, inplace=True)
df_plank['Rank'] = np.arange(start=1, stop=df_plank.shape[0] + 1, step=1) 
df_plank.set_index('Rank', inplace=True)

# create nice styler object
df_plank_nice = df_plank.rename(columns={'goal_time': 'Ziel_Zeit',
                                         'eff_time': 'Effektive_Zeit',
                                         'goal_achieved': 'Ziel_Erreicht',
                                         'goal_diff': 'Differenz'})
df_plank_nice = df_plank_nice.style.apply(highlight_goal_achieved, axis=1)
df_plank_nice.format(
    {
        "Ziel_Zeit": lambda x: x.strftime("%Mmin %Ss"),
        "Effektive_Zeit": lambda x: x.strftime("%Mmin %Ss"),
    }
)

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