import streamlit as st
import preprocessor , helper
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image
)
from reportlab.lib.styles import getSampleStyleSheet
st.set_page_config(
    page_title="AnalyzU",
    layout="wide"
)
if 'analysis_viewed' not in st.session_state:
    st.session_state.analysis_viewed = False
st.sidebar.title("AnalyzU")
uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is None:
    st.title("ChatInsight: Advanced WhatsApp Analytics")
    st.subheader("Transform raw chat transcripts into behavioral intelligence.")
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown("###  How to Get Started")
        st.markdown("""
        1. **Open WhatsApp** on your mobile device and navigate to your target group or individual chat.
        2. Tap the **three vertical dots (Android)** or **Group/Contact Name (iOS)** -> Select **More** ->**Export Chat**.
        3. Choose **Without Media** (this application is optimized for hyper-fast text parsing metrics).
        4. Drag and drop the exported `.txt` file directly into the sidebar uploader workspace.
        """)
        
        # Privacy Expandable Box
        with st.expander("Read Our Data Privacy Guarantee", expanded=True):
            st.markdown("""
            * **In-Memory Volatile Processing:** Your uploaded text file is processed strictly within server RAM. We do not provision databases or local persistent storage.
            * **Session Isolation:** The moment you close or refresh this browser tab, your chat instance memory allocation is completely wiped clean automatically.
            * **Enterprise API Isolation:** AI text summarization is routed via the **Google Gemini Developer API**. Under enterprise terms, your chat data is **never** used for model training or saved by external servers.
            """)
        
    with col2:
        st.markdown("### Don't have a file ready?")
        st.info("Test-drive the analytics engine right now using our pre-cleaned sample group dataset.")
        
        # Note: Ensure you have a 'sample_chat.txt' file in your local folder so this doesn't crash!
        try:
            with open("chat.txt", "rb") as file:
                st.download_button(
                    label="Download Sample Chat Log",
                    data=file,
                    file_name="sample_whatsapp_chat.txt",
                    mime="text/plain",
                    width="stretch"
                )
        except FileNotFoundError:
            st.warning("Sample file 'sample_chat.txt' missing from root directory. Please place a dummy chat log here.")
else :
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)
    st.dataframe(df)    
    user_list = df['Author'].unique().tolist()
    user_list.sort()
    user_list.insert(0, "Overall")
    selected_user = st.sidebar.selectbox("Select User", user_list)
    if st.sidebar.button("Show Analysis"):
        st.session_state.analysis_viewed = True
    if st.session_state.analysis_viewed :    
        col1, col2, col3, col4 = st.columns(4)
        total_messages, words, media_shared, links_shared = helper.fetch_stats(selected_user, df)
        with col1:
            st.metric(label="Total Messages", value=total_messages)

        with col2:
            st.metric(label="Total Words", value=words)

        with col3:
            st.metric(label="Media Shared", value=media_shared)

        with col4:
            st.metric(label="Links Shared", value=links_shared)
        st.markdown("---")
        st.subheader("Daily Message Trajectory")
        fig_time = helper.get_daily_timeline_plotly(selected_user, df)
        st.plotly_chart(fig_time, width="stretch") 
        if(selected_user == 'Overall'):
            col1, col2 = st.columns([2, 1]) 
            with col1:
                st.subheader("Participant Engagement : Top Contributors")
                top_users = df['Author'].value_counts().head(10)
                fig_active = px.bar(top_users, x=top_users.values, y=top_users.index, template = 'plotly_dark', labels = {'x' : 'Active Users', 'y' : 'Message count'});
                st.plotly_chart(fig_active, width="stretch")
            with col2:
                st.subheader("Contribution %")
                x, busy_user_df = helper.busy_users(selected_user, df)   
                st.dataframe(busy_user_df, width="stretch", hide_index = True)  

        st.subheader('Monthly Interaction Distribution')
        fig_heatmap = helper.monthly_heatmap(selected_user, df) 
        st.plotly_chart(fig_heatmap, width="stretch")
        
        st.title("What We Actually Talk About...")
        df_wc = helper.create_wordcloud(selected_user,df)
        if df_wc is None:
             st.warning(f"{selected_user} has 0 words available to build a cloud (only media or deleted messages found).")
        else:
            fig_wc ,ax = plt.subplots()
            ax.axis("off")
            ax.imshow(df_wc)
            st.pyplot(fig_wc)

        col5, col6 = st.columns(2)
        with col5:
            fig_days = helper.active_days(selected_user, df)  
            st.plotly_chart(fig_days, width="stretch")
        with col6 : 
            fig_dates = helper.active_dates(selected_user, df)    
            st.plotly_chart(fig_dates, width="stretch")

        fig_emoji = helper.emoji_analysis(selected_user, df)    
        st.plotly_chart(fig_emoji, width="stretch")

        st.subheader("Peak Active Hours")
        fig_hour = helper.get_active_hours_plotly(selected_user, df)
        st.plotly_chart(fig_hour,width="stretch") 

        st.subheader("Conversational Tone & User Sentiment Profiles")
        fig_sentiment, user_sentiment_df = helper.analyze_chat_sentiment(selected_user, df)
        if user_sentiment_df is None:
            st.warning(" No active text data found to perform text sentiment analysis.")
        else:
         
            sent_col1, sent_col2 = st.columns(2)
            
            with sent_col1:
                if fig_sentiment is None:
                    st.info(f"{selected_user} hasn't sent any scorable text messages yet.")
                else:
                
                    st.plotly_chart(fig_sentiment, width="stretch")
                    
            with sent_col2:
                st.markdown("<br>", unsafe_allow_html=True) 
                st.write("### Group Members Sentiment Breakdown")
                
               
                st.dataframe(
                    user_sentiment_df, 
                    use_container_width=True, 
                    hide_index=True
                )
        if(st.button("Generate report")) :
            pdf = SimpleDocTemplate("chat_report.pdf")
            styles = getSampleStyleSheet()
            elements = []
            elements.append(Paragraph("WhatsApp Chat Analysis Report", styles['Title']))

            fig_time.write_image("time.png")
            elements.append(Image("time.png", width=450, height=250))
            elements.append(Spacer(1,20))
            if(selected_user == 'Overall'):
                fig_active.write_image("active_users.png")
                elements.append(Image("active_users.png", width=450, height=250))
                elements.append(Spacer(1,20))
            
            fig_heatmap.write_image("heatmapp.png")
            elements.append(Image("heatmapp.png", width=450, height=250))
            elements.append(Spacer(1,20))

            fig_emoji.write_image("emoji.png")
            elements.append(Image("emoji.png", width=450, height=250))
            elements.append(Spacer(1,20))

            # fig_wc.write_image("wc.png")
            fig_hour.write_image("hour.png")
            elements.append(Image("hour.png", width=450, height=250))
            elements.append(Spacer(1,20))

            fig_sentiment.write_image("sentiment.png")
            elements.append(Image("sentiment.png", width=450, height=250))
            elements.append(Spacer(1,20))
            
            pdf.build(elements)
            st.success("Report Generated")
            with open("chat_report.pdf", "rb") as pdf_file:
                st.download_button(
                    label="Download Report",
                    data=pdf_file,
                    file_name="chat_report.pdf",
                    mime="application/pdf",
                   width="stretch"
                )

            st.markdown("---")
        st.header("Intelligent Chat Insights")
        with st.expander("Generate AI Chat Summary & Key Takeaways", expanded=False):
            if st.button("Analyze with Gemini AI"):
                with st.spinner("Gemini is analyzing the conversation threads... Please wait."):
                    summary_result = helper.summarize_chat_with_gemini(selected_user, df)
                    if  "error" in summary_result.lower():
                        st.error(summary_result)  
                    else:
                        st.success("Analysis Complete!")
                        st.markdown("### Executive Summary")
                        st.markdown(summary_result)