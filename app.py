#MOVIE RECCOMENDATION SYSTEM

from flask import Flask, render_template, request, jsonify
import recommender
import os
import pandas as pd
#flask activate
app = Flask(__name__)

# Load movie data
if not os.path.exists('data/movies.csv'):
    os.makedirs('data/movies', exist_ok=True)
    # Create a sample dataset if none exists
    recommender.create_sample_dataset()

movie_data = pd.read_csv('data/movies.csv')
rec_engine = recommender.MovieRecommender(movie_data)

# User context storage (in a real app, use a database)
user_contexts = {}

@app.route('/')
def index():   #for main page
    """Render the main page"""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Process chat messages and return recommendations"""
    data = request.json
    user_id = data.get('user_id', 'default_user')
    message = data.get('message', '').strip()
    
    # Get or create user context
    if user_id not in user_contexts:
        user_contexts[user_id] = recommender.UserContext()
    
    user_context = user_contexts[user_id]
    
    # Generate response
    response, recommendations = rec_engine.process_message(message, user_context)
    
    return jsonify({
        'response': response,
        'recommendations': recommendations
    })
#reseting the context
@app.route('/reset', methods=['POST'])
def reset_context(): #resets the context
    """Reset user preferences"""
    data = request.json
    user_id = data.get('user_id', 'default_user')
    
    if user_id in user_contexts:
        user_contexts[user_id] = recommender.UserContext()
    
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True)