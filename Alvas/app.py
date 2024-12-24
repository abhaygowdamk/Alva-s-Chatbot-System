import nltk
import string
import pandas as pd
from flask import Flask, request, jsonify, render_template
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk import ne_chunk, pos_tag
import json

# Initialize Flask app
app = Flask(__name__)

# Ensure necessary NLTK packages are downloaded
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('averaged_perceptron_tagger_eng')
nltk.download('maxent_ne_chunker_tab')

# Initialize Lemmatizer
lemmatizer = WordNetLemmatizer()

# Load intents from JSON file
def load_intents():
    with open('intents.json') as file:
        intents = json.load(file)
    return intents

# College-CSV Mapping (Map colleges to CSV files)
college_csv_mapping = {
    "Alva's College of Naturopathy & Yogic Sciences": "alvas_college_of_naturopathy_and_yogic_sciences.csv",
    "Alva's Degree College": "alvas_degree_college.csv",
    "Alva's Homeopathic College": "alvas_homeopathic_college.csv",
    "Alva's Institute of Engineering and Technology": "alvas_institute_of_engineering_and_technology.csv",
    "Alva's MBA": "alvas_mba.csv",
    "Alva's PU College": "alvas_pu_college.csv"
}

# Define function for text preprocessing
def preprocess_text(text):
    text = text.lower()
    tokens = word_tokenize(text)
    tokens = [word for word in tokens if word not in string.punctuation]
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    return tokens

# Named Entity Recognition (NER)
def extract_entities(text):
    tokens = word_tokenize(text)
    tagged = pos_tag(tokens)
    tree = ne_chunk(tagged)
    entities = [" ".join(word for word, tag in subtree) for subtree in tree if isinstance(subtree, nltk.Tree)]
    return entities

# Extract college name using entity recognition
def extract_college_from_text(text):
    entities = extract_entities(text)
    for entity in entities:
        for college in college_csv_mapping:
            if college.lower() in entity.lower():
                return college_csv_mapping[college]
    return None

# Load college data from CSV
def get_college_data(csv_file, data_type="Contact Details"):
    try:
        file_path = f'static/{csv_file}.csv'  # Add .csv extension
        data = pd.read_csv(file_path)
        if data_type == "Contact Details":
            contact_details = data.iloc[0].get('Contact Details', 'No contact details available.')
            return contact_details
        elif data_type == "About":
            about_info = data.iloc[0].get('About', 'No information available.')
            return about_info
    except Exception as e:
        print(f"Error loading CSV file from {file_path}: {e}")
        return "Sorry, I couldn't fetch data for this college."

# Intent Mapping Function
def get_intent(message, intents_data):
    processed_message = preprocess_text(message)
    for intent in intents_data['intents']:
        for example in intent['examples']:
            processed_example = preprocess_text(example)
            if any(word in processed_message for word in processed_example):
                return intent['intent']
    return "unknown"

# Generate bot response dynamically
def generate_response(intent, message, selected_college_csv):
    if intent == "contact_details":
        if selected_college_csv:
            return get_college_data(selected_college_csv, "Contact Details")
        else:
            return "Please select a college to get the contact details."
    elif intent == "about_college":
        if selected_college_csv:
            return get_college_data(selected_college_csv, "About")
        else:
            return "Please select a college to get more information."
    else:
        return "I couldn't understand your request. Please try again."


# Define the /get_response route to handle user queries
@app.route('/get_response', methods=['POST'])
def get_response():
    user_data = request.get_json()
    user_message = user_data.get('message')
    selected_college = user_data.get('college')

    if not user_message or not selected_college:
        return jsonify({'response': "Please provide a message and select a college."})

    intents = load_intents()
    preprocessed_message = preprocess_text(user_message)
    intent = get_intent(user_message, intents)
    college_csv_file = extract_college_from_text(user_message) or selected_college
    bot_response = generate_response(intent, user_message, college_csv_file)
    
    return jsonify({'response': bot_response})

# Serve the main page
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)