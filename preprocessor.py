import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
from pathlib import Path
def preprocess(dataset):
    strict_message_pattern = r'^(\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s?[aApP][mM])\s-\s([^:]+):\s(.*)$'
    timestamp_pattern = r'^(\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s?[aApP][mM])\s-'
   

    data = []
    for line in dataset.splitlines():
        if re.match(timestamp_pattern, line):
            match = re.match(strict_message_pattern, line)
            if match:
                date_time, author, message = match.groups()
                data.append([date_time, author, message])
        else:
            if data:
                data[-1][2] += " " + line.strip()
    df = pd.DataFrame(data, columns=['DateTime', 'Author', 'Message'])
    df['DateTime'] = df['DateTime'].str.replace(r'\s+', ' ', regex=True)
    time_12h = pd.to_datetime(df['DateTime'], format='%m/%d/%y, %I:%M %p', errors='coerce')
    time_24h = pd.to_datetime(df['DateTime'], format='%m/%d/%y, %H:%M', errors='coerce')
    df['DateTime'] = time_12h.fillna(time_24h)
    df['Year'] = df['DateTime'].dt.year
    df['Month'] = df['DateTime'].dt.month_name()
    df['Day'] = df['DateTime'].dt.day_name()
    df['Time'] = df['DateTime'].dt.time
    df['Date'] = df['DateTime'].dt.date
    df['Hour'] = df['DateTime'].dt.hour
    return df