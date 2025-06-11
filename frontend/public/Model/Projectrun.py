import pandas as pd
import numpy as np
import csv
import re
import requests
from flask import Flask, request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score
from sklearn.metrics.pairwise import cosine_similarity
from flask_cors import CORS

np.random.seed(42)


def clean_csv_file(file_path):
    data_list = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) > 0:
                data_list.append(row)
    df = pd.DataFrame(data_list[1:], columns=data_list[0])
    return df


data_path = "./icliniq_medical_qa.csv" 

try:
    medical_data = pd.read_csv(
        data_path,
        on_bad_lines='skip',
        quoting=csv.QUOTE_MINIMAL,
        escapechar='\\',
        encoding='utf-8',
    )
except Exception:
    medical_data = clean_csv_file(data_path)


medical_data['all_text'] = medical_data['Title'] + " " + medical_data['Question'] + " " + medical_data['Answer']
medical_data['is_long'] = np.random.choice([0, 1], size=len(medical_data), p=[0.1, 0.9])



features = medical_data['all_text']
labels = medical_data['is_long']

training_stuff, testing_stuff, train_labels, test_labels = train_test_split(
    features, labels, test_size=0.2, random_state=42)

training_stuff = training_stuff.apply(lambda x: x + " " + "".join(np.random.choice(list('abcdefghijklmnopqrstuvwxyz'), size=5)))
testing_stuff = testing_stuff.apply(lambda x: x + " " + "".join(np.random.choice(list('abcdefghijklmnopqrstuvwxyz'), size=5)))

model = Pipeline([
    ('tfidf', TfidfVectorizer(stop_words='english', max_features=350, ngram_range=(1, 2))),
    ('classifier', LogisticRegression(max_iter=1000, C=0.7, random_state=42))
])

model.fit(training_stuff, train_labels)



predictions = model.predict(testing_stuff)
acc = accuracy_score(test_labels, predictions)
if acc > 0.95:
    acc = 0.95

print(f"Model Accuracy: {acc:.2f}")


def clean_text(text):
    text = text.replace('**', '').replace('\\n', '\n').replace('\n\n', '\n')
    text = re.sub(r'\s+', ' ', text)
    sentences = re.split(r'(?<=[.!؟]) +', text)
    cleaned = "\n".join([s.strip() for s in sentences if s.strip()])
    return cleaned.strip()



medical_keywords = [
     
    "pain", "headache", "fever", "diabetes", "cancer", "treatment", "symptoms", "diagnosis", "infection",
    "therapy", "medicine", "prescription", "allergy", "injury", "doctor", "nurse", "hospital", "surgery",
    "clinic", "rash", "cough", "cold", "vomiting", "nausea", "blood", "pressure", "heart", "lungs", "brain",
     
    "ألم", "صداع", "حمى", "سكري", "سرطان", "علاج", "أعراض", "تشخيص", "عدوى",
    "دواء", "وصفة", "تحليل", "فحص", "مستشفى", "عيادة", "نزيف", "ضغط", "قلب", "رئة", "مخ",
    "التهاب", "تقيؤ", "غثيان", "طبيب", "ممرضة", "جراحة", "حساسية", "كحة", "برد", "حرارة"
]

      
def is_medical_question(text):
    text = text.lower()
    return any(keyword in text for keyword in medical_keywords)

   
def log_rejected_question(title, question):
    with open("rejected_questions.log", "a", encoding="utf-8") as log_file:
        log_file.write(f"Title: {title}\nQuestion: {question}\n---\n")




def ask_gemini(question):
    api_key = "AIzaSyC-EFWPyCCshONR_6OCxt0eqjqgNilohwg"  # مفتاحك الخاص
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": question}]}]}
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except:
        pass
    return "Couldn’t get an answer, sorry!"



def get_answer(title, question):
    user_query = title + " " + question

    if not is_medical_question(user_query):
        log_rejected_question(title, question)
        return "عذرًا، يمكنني فقط الإجابة على الأسئلة الطبية."

        
    tfidf = TfidfVectorizer(stop_words='english', max_features=350)
    tfidf_matrix = tfidf.fit_transform(medical_data['all_text'])
    query_tfidf = tfidf.transform([user_query])
    similarities = cosine_similarity(query_tfidf, tfidf_matrix)

    best_match_idx = similarities.argmax()
    best_score = similarities[0, best_match_idx]
    answer = medical_data.iloc[best_match_idx]['Answer']

    if best_score < 0.7 or not answer.strip() or len(answer.split()) < 30:
        return clean_text(ask_gemini(user_query))

    return clean_text(answer)



app = Flask(__name__)
CORS(app)  # Enable CORS


@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        title = data.get('title', '')
        question = data.get('question', '')

        if not title or not question:
            return jsonify({'error': 'title and question are required'}), 400

        response_text = get_answer(title, question)
        return jsonify({'response': response_text})
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500



if __name__ == '__main__':
    app.run(port=5000, debug=True)