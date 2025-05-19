# Movie Recommendation Chat System

A conversational movie recommendation system that allows users to chat about their movie preferences and receive personalized film recommendations.

![Movie Recommendation System Screenshot](https://via.placeholder.com/800x450?text=Movie+Recommendation+System)

## Features

- **Natural Language Interface**: Chat with the system about your movie preferences
- **Intelligent Recommendation Engine**: Provides personalized movie recommendations based on your preferences
- **Real-time Updates**: Instantly see recommendations as you chat
- **Preference Learning**: System learns from your interactions and refines recommendations over time
- **User-friendly Interface**: Clean, responsive design for desktop and mobile
- **Preference Reset**: Easily reset preferences to start fresh

## How It Works

The system extracts preferences from natural language conversations, including:
- Genre preferences (action, comedy, drama, etc.)
- Time period preferences (recent films, classics, specific years)
- Specific movie mentions
- Positive and negative feedback

Based on these extracted preferences, the system scores movies in its database and recommends the most relevant ones.

## Installation

### Prerequisites

- Python 3.7+
- pip (Python package manager)

### Step 1: Clone the repository

```bash
git clone https://github.com/yourusername/movie-recommendation-chat.git
cd movie-recommendation-chat
```

### Step 2: Set up a virtual environment (recommended)

```bash
python -m venv venv
```

Activate the virtual environment:

- On Windows:
  ```bash
  venv\Scripts\activate
  ```
- On macOS/Linux:
  ```bash
  source venv/bin/activate
  ```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run the application

```bash
python app.py
```

The application will start and be available at `http://127.0.0.1:5000/`

## Usage

1. **Start Chatting**: Tell the system what kinds of movies you enjoy
2. **Explore Recommendations**: View movie recommendations that appear on the right side
3. **Refine Preferences**: Continue the conversation to get more tailored recommendations
4. **Click on Movies**: Click on a recommended movie to express interest in similar films
5. **Reset Preferences**: Use the reset button to start fresh

### Example Conversations

- "I like action movies from the 2010s"
- "I enjoyed The Dark Knight and Inception"
- "I prefer sci-fi but not horror"
- "Show me classic movies from the 80s"
- "I want to see something with comedy and romance"

## Project Structure

```
movie-recommendation-system/
├── app.py                 # Main Flask application
├── static/                # Static files
│   ├── css/
│   │   └── style.css      # CSS styling
│   └── js/
│       └── script.js      # Frontend JavaScript
├── templates/             # HTML templates
│   └── index.html         # Main page template
├── recommender.py         # Recommendation engine
├── data/                  # Data files
│   └── movies.csv         # Sample movie dataset
└── requirements.txt       # Project dependencies
```

## Customization

### Adding More Movies

The system comes with a sample dataset of 50 movies. To add more movies:

1. Create a CSV file with the following columns:
   - movie_id: Unique identifier
   - title: Movie title
   - year: Release year
   - genres: Pipe-separated list of genres (e.g., "action|adventure|sci-fi")
   - popularity: Popularity score (higher is more popular)

2. Replace the `data/movies.csv` file with your dataset

### Modifying the Recommendation Algorithm

The recommendation algorithm is defined in `recommender.py`. You can modify:

- `extract_preferences()`: How preferences are extracted from messages
- `get_recommendations()`: How movies are scored and selected
- `generate_response()`: How responses are formatted

