
# 📊 AnalyzU – WhatsApp Chat Analytics Dashboard

**Live Demo:** [https://analyzu.streamlit.app/]

AnalyzU is an interactive **WhatsApp Chat Analyzer** built with **Python, Streamlit, Pandas, Plotly, and Generative AI**. It transforms exported WhatsApp chat logs into meaningful insights through advanced visualizations, sentiment analysis, activity tracking, and AI-generated summaries.

The application supports both **individual chats** and **group conversations** while maintaining user privacy through in-memory processing.

---

## ✨ Features

### 📈 Chat Statistics

* Total messages exchanged
* Total words used
* Media shared count
* Links shared count

### 📅 Activity Analysis

* Daily message timeline
* Monthly interaction trends
* Most active dates
* Most active weekdays
* Peak chat hours analysis

### 👥 User Participation Insights

* Top contributors in group chats
* User contribution percentages
* Individual participant analysis

### ☁️ Word Cloud Generation

* Frequently used words visualization
* Hinglish stop-word filtering support

### 😀 Emoji Analytics

* Most frequently used emojis
* Emoji usage distribution

### 😊 Sentiment Analysis

* Positive, Neutral, and Negative message classification
* User-wise sentiment breakdown
* Conversation mood visualization

### 🤖 AI-Powered Insights

* Chat summarization using Google Gemini
* Automated key takeaways from conversations

### 📄 PDF Report Export

Generate downloadable analysis reports containing:

* Timelines
* Activity charts
* Sentiment analysis
* User engagement metrics

---

## 🛠️ Tech Stack

| Category        | Technologies                |
| --------------- | --------------------------- |
| Frontend        | Streamlit                   |
| Data Processing | Pandas, NumPy               |
| Visualization   | Plotly, Matplotlib, Seaborn |
| NLP             | TextBlob                    |
| Word Cloud      | WordCloud                   |
| AI Integration  | Google Gemini API           |
| Reporting       | ReportLab                   |

---

## 🚀 How It Works

1. Export a WhatsApp chat (**Without Media**).
2. Upload the `.txt` file to AnalyzU.
3. Select:

   * Overall Chat Analysis
   * Individual Participant Analysis
4. Explore interactive insights and visualizations.
5. Generate AI summaries and export PDF reports.

---

## 📂 Project Structure

```text
AnalyzU/
│
├── app.py                # Streamlit application
├── helper.py             # Analytics functions
├── preprocessor.py       # WhatsApp chat preprocessing
├── stop_hinglish.txt     # Custom stopwords
├── requirements.txt
├── sample_chat.txt
└── README.md
```

---

## 🔒 Privacy First

* Uploaded chats are processed in-memory.
* No permanent storage of user conversations.
* Session data is cleared when the browser session ends.
* AI summaries are generated through Google Gemini API.

---

## ⚙️ Installation

```bash
git clone https://github.com/your-username/analyzu.git

cd analyzu

pip install -r requirements.txt

streamlit run app.py
```

---

## 📌 Future Improvements

* Advanced NLP-based topic extraction
* Conversation clustering
* Toxicity detection
* Chatbot-based insights
* Machine Learning prediction models
* Multi-language sentiment analysis

---

## 👩‍💻 Author

**Banala Vasanthi Laxmi Reddy**
B.Tech CSE, IIITDM Jabalpur

GitHub: [https://github.com/vasanthilaxmi]
LinkedIn: [linkedin.com/in/vasanthi-laxmi-banala]

---
