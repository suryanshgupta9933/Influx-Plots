# Importing Dependencies

import os
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.markers import MarkerStyle
import seaborn as sns
import plotly.express as px
import io
import base64
from flask import render_template
import warnings
warnings.filterwarnings('ignore')

# Reading and Preprocessing the CSV file

def read_csv_file(file_path):
    df = pd.read_csv(file_path)
    df["dates"] = df["_time"].str[:10]
    df = df.drop(labels=["result", "table", "_start", "_stop",
                         "_measurement", "domain_id", "server"], axis=1)
    df = df.drop(labels=["_time"], axis=1)
    dates = df.dates.unique()
    agent_ids = df.agent_id.unique()
    agent_ids.sort()
    fields = ["backup", "restore", "connection"]
    return df, dates, agent_ids, fields

# Transforming the Dataframe into a Dictionary

def df_to_dict(df, dates, agent_ids, fields):
    value = []
    time = []
    tree = {date: {agent_id: {field: {} for field in fields}
                   for agent_id in agent_ids} for date in dates}
    for date in dates:
        for agents in agent_ids:
            for field in fields:
                value.append(df.query(
                    "dates == @date and agent_id == @agents and _field == @field")["_value"].sum())
                time.append(df.query(
                    "dates == @date and agent_id == @agents and _field == @field")["dates"].count() * 30)
                tree[date][agents][field] = {
                    "value": value.pop(0), "time": time.pop(0)}
    return tree

# Data Manipulation

def data_manipulation(df, dates, agent_ids, fields, f):
    agentss = []
    datess = []
    fieldss = []
    values = []
    times = []
    dict = {}
    for date in dates:
        for agents in agent_ids:
            for field in fields:
                values.append(df.query(
                    "dates == @date and agent_id == @agents and _field == @field")["_value"].sum())
                times.append(df.query(
                    "dates == @date and agent_id == @agents and _field == @field")["dates"].count() * 30)
                fieldss.append(field)
                datess.append(date)
                agentss.append(agents)
    tree = {"Date": datess, "Agents": agentss,
            "Fields": fieldss, "Value": values, "Time": times}
    df = pd.DataFrame.from_dict(tree)
    df = df.query("Fields == @f")
    mean_value = np.mean(df.Value)
    mean_time = np.mean(df.Time)
    df["New_Value"] = df["Value"] - mean_value
    df["New_Time"] = df["Time"] - mean_time
    return df

# Plotting the Graphs

def plot_graphs(df):
    plt.figure(figsize=(8, 6))
    sns_plot = sns.scatterplot(x="New_Time", y="New_Value",
                           hue="Agents", alpha=0.6, s=100, data=df)
    sns_plot.set(xlabel='Time', ylabel='Value')
    plt.axhline(y=0, color='k', linestyle='--', linewidth=1)
    plt.axvline(x=0, color='k', linestyle='--', linewidth=1)
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    image_base64 = base64.b64encode(image_png).decode('utf-8')
    image = f"data:image/png;base64,{image_base64}"
    return image