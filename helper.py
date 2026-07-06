from urlextract import  URLExtract
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import re
from wordcloud import WordCloud
from collections import Counter
import emoji
import plotly.express as px
import plotly.graph_objects as go
from textblob import TextBlob
import os
from google import genai

def fetch_stats(selected_user, df):
    if selected_user != 'Overall':
       new_df =  df[df['Author'] == selected_user]
    else :
       new_df = df.copy()   
    total_msgs = new_df.shape[0]
    words = []
    for message in new_df['Message']:
       words.extend(message.split())
    num_media_messages = new_df[new_df['Message'] == '<Media omitted>'].shape[0]    
    links = []
    extract = URLExtract()
    for message in new_df['Message']:
        links.extend(extract.find_urls(message))
    return total_msgs, len(words), num_media_messages, len(links)

def busy_users(selected_user, df):
    if selected_user != 'Overall':
       new_df =  df[df['Author'] == selected_user]
    else :
       new_df = df.copy() 
    x = new_df['Author'].value_counts().head()
    busy_user_df = round((new_df['Author'].value_counts() / new_df.shape[0]) * 100, 2).reset_index().rename(columns={'index': 'Name', 'Author': 'Percent'})
    return x, busy_user_df   

def monthly_heatmap(selected_user, df):
    if selected_user != 'Overall':
       new_df =  df[df['Author'] == selected_user].copy()
    else :
       new_df = df.copy()  
    month_order = [
        'January', 'February', 'March', 'April',
        'May', 'June', 'July', 'August',
        'September', 'October', 'November', 'December'
    ]
    
    new_df['Month'] = pd.Categorical(
        new_df['Month'],
        categories=month_order,
        ordered=True
    )
    heat_df = (
        new_df.groupby(['Year', 'Month'])
        .size()
        .reset_index(name='Message_Count')
        .pivot(index='Year', columns='Month', values='Message_Count')
        .fillna(0)
        .astype(int)
    )
    fig = go.Figure(data=go.Heatmap(
        z=heat_df.values,
        x=heat_df.columns.tolist(),
        y=heat_df.index.tolist(),
        colorscale='Blues',
        text=heat_df.values,
        texttemplate="%{text}", # Force numbers to show inside cells natively
        hovertemplate="Year: %{y}<br>Month: %{x}<br>Messages: %{z}<extra></extra>"
    ))
    
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Year",
        template="plotly_dark", 
        height=400
    )
    
    return fig

def active_days(selected_user, df) :
    if selected_user != 'Overall':
       new_df =  df[df['Author'] == selected_user]
    else :
       new_df = df.copy() 
    active_day = new_df.groupby('Day').size().reset_index(name='Message_Count')
    day_order = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    fig = px.bar(
        active_day, 
        x='Day', 
        y='Message_Count',
        title='Most Active Days of the Week',
        template='plotly_dark'
    )
    fig.update_traces(marker_color='steelblue', hovertemplate="Day: %{x}<br>Messages: %{y}<extra></extra>")
    fig.update_layout(xaxis_title="Day of the Week", yaxis_title="Message Count", height=400)
    fig.update_xaxes(tickangle = -45, categoryorder='array', categoryarray=day_order)
    return fig

def active_dates(selected_user, df) :
    if selected_user != 'Overall':
       new_df =  df[df['Author'] == selected_user]
    else :
        new_df = df.copy() 
    active_date = new_df.groupby('Date').size().reset_index(name='Message_Count').sort_values(by='Message_Count', ascending=False).head(10)
    fig = px.bar(
    active_date,
    x='Date',
    y='Message_Count',
    color='Message_Count', 
    # color_continuous_scale='Blues_r',
    title='Top 10 Most Active Dates',
    template='plotly_dark'
    )
    fig.update_traces(
    marker_color='steelblue',    
    hovertemplate="Date: %{x}<br>Messages: %{y}<extra></extra>"
)
    fig.update_layout(height=400)
    fig.update_xaxes(type = 'category', tickangle= -45) 
    
    return fig
 
def remove_stop_words(message):
    with open('stop_hinglish.txt', 'r') as f :
        stop_words = f.read()
    y = []
    for word in message.lower().split():
        if word not in stop_words:
            y.append(word)
    return " ".join(y)     
def create_wordcloud(selected_user,df):

    if selected_user != 'Overall':
        new_df = df[df['Author'] == selected_user]
    else :
        new_df = df.copy()
    temp = new_df[new_df['Author'] != 'group_notification']
    system_phrases = 'omitted|deleted|edited|media|this message was'
    temp = temp[~temp['Message'].str.contains(system_phrases, case=False, na=False)]
    if(temp.shape[0] == 0) :
        return None
    wc = WordCloud(width=500,height=500,min_font_size=10,background_color='Black')
    temp['Message'] = temp['Message'].apply(remove_stop_words)
    combined_text = temp['Message'].str.cat(sep=" ")
    if not combined_text.strip():
        return None
    df_wc = wc.generate(combined_text)
    return df_wc 
def emoji_analysis(selected_user, df) :
    st.title('Top 10 Most Used Emojis')
    if selected_user != 'Overall':
       new_df =  df[df['Author'] == selected_user]
    else :
       new_df = df.copy() 
    emojis = []

    for msg in new_df['Message'].astype(str):
        extracted_items = emoji.emoji_list(msg)
        for item in extracted_items : 
            emojis.append(item['emoji'])

    emoji_count = Counter(emojis)
    top_emojis = emoji_count.most_common(10)
    if not top_emojis:
        fig_emoji = px.bar(title="No Emojis Found in this Chat Log", template='plotly_dark')
        fig_emoji.update_layout(height=400)
        return fig_emoji
    emoji_df = pd.DataFrame(top_emojis, columns=['Emoji', 'Count'])
    emoji_df['Emoji_desc'] = emoji_df['Emoji'].apply(lambda x: emoji.demojize(x)[1:-1])
    fig_emoji = px.bar(emoji_df, x= 'Count', y='Emoji_desc',orientation = 'h', color = 'Count', color_continuous_scale = 'Purples',  template = 'plotly_dark')
    fig_emoji.update_layout(
        xaxis_title="Usage Count", 
        yaxis_title="Emoji Label", 
        coloraxis_showscale=False,
        height=400,
        yaxis={'categoryorder': 'total ascending'}
    )
    return fig_emoji
def get_daily_timeline_plotly(selected_user, df):
    if selected_user != 'Overall':
        new_df = df[df['Author'] == selected_user]
    else:
        new_df = df.copy()  
    timeline_data = new_df.groupby('Date').size().reset_index(name='Message_Count')

    fig = px.line(
        timeline_data, x='Date', y='Message_Count',
        labels={'Date': 'Timeline', 'Message_Count': 'Messages Sent'},
        template="plotly_dark"
    )
    fig.update_traces(line_color='#1f77b4', line_width=2)
    return fig

def get_active_hours_plotly(selected_user, df):
    if selected_user != 'Overall':
        new_df = df[df['Author'] == selected_user]
    else:
        new_df = df.copy() 
    hourly_data = new_df.groupby('Hour').size().reset_index(name='Message_Count')
    
    fig = px.bar(
        hourly_data, x='Hour', y='Message_Count',
        labels={'Message_Count': 'Messages Count', 'Hour': 'Hour of Day (24hr)'},
        template="plotly_dark"
    )
    fig.update_xaxes(tickvals=list(range(0, 24)))
    fig.update_traces(marker_color='skyblue')
    return fig



def analyze_chat_sentiment(selected_user, df):
    if selected_user != 'Overall':
        new_df = df[df['Author'] == selected_user]
    else:
        new_df = df.copy()

    temp = new_df[new_df['Author'] != 'group_notification'].copy()
    temp = temp[~temp['Message'].str.contains('omitted|media|deleted|edited', case=False, na=False)]
    if temp.shape[0] == 0:
        return None
    with open('stop_hinglish.txt', 'r') as f:
        stop_words = f.read().splitlines()
    def get_message_sentiment(message):
        analysis = TextBlob(str(message))
        polarity = analysis.sentiment.polarity
        words = []
       
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)
        cleaned_words = " ".join(words)  
        if not cleaned_words.strip() :
            return 'Neutral'      
        if polarity > 0:
            return 'Positive'
        elif polarity < 0:
            return 'Negative'
        else:
            return 'Neutral'

    temp['Sentiment'] = temp['Message'].apply(get_message_sentiment)

    sentiment_counts = temp['Sentiment'].value_counts().reset_index()
    sentiment_counts.columns = ['Vibe', 'Count']

    color_map = {'Positive':'#2ecc71', 'Neutral': '#95a5a6', 'Negative': '#e74c3c'}

    fig = px.pie(
        sentiment_counts,
        names='Vibe',
        values='Count',
        # hole=0.4, # Cuts out the center core to make a premium donut shape
        color='Vibe',
        color_discrete_map=color_map,
        title=f"Chat Sentiment Analysis Distribution ({selected_user})",
        template='plotly_dark'
    )

    fig.update_layout(
        margin=dict(t=50, b=20, l=20, r=20),
        legend_title_text='Conversation Mood'
    )
    user_matrix = (temp.groupby(['Author', 'Sentiment']).size().unstack(fill_value = 0).reset_index())
    
    for col in ['Positive', 'Neutral', 'Negative'] :
        if col not in user_matrix.columns :
            user_matrix[col] = 0
    user_matrix = user_matrix[['Author', 'Positive', 'Neutral', 'Negative']]
    user_matrix.columns = ['User Name', 'Positive Msgs', 'Neutral Msgs', 'Negative Msgs']
    user_matrix = user_matrix.sort_values(by='Positive Msgs', ascending=False)        
    return fig, user_matrix

def summarize_chat_with_gemini(selected_user, df):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "Gemini API Key not found! Please set the GEMINI_API_KEY environment variable."
    client = genai.Client(api_key=api_key)
    if selected_user != 'Overall':
        new_df = df[df['Author'] == selected_user]
    else:
        new_df = df.copy()
    temp = new_df[new_df['Author'] != 'group_notification'].copy()
    temp = temp[~temp['Message'].str.contains('omitted|media|deleted|edited', case=False, na=False)]

    transcript = ""
    for index, row in temp.head(500).iterrows():
        transcript += f"{row['Author']}: {row['Message']}\n"

    if not transcript.strip():
        return "Not enough text data available to generate a summary."

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=(
            f"You are an expert chat analyzer. Review the following WhatsApp chat log "
            f"for '{selected_user}'. Provide a high-level bulleted summary detailing the "
            f"main topics discussed, the general emotional tone, and key decisions or takeaways:\n\n{transcript}"
             )
 )
        return response.text
    except Exception as e:
        return f"An error occurred while generating the summary: {e}"
