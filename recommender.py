#MOVIE RECOMMENDATION SYSTEM

import pandas as pd
import numpy as np
import re
import os
from collections import defaultdict

class UserContext:
    """Stores user preferences and conversation history"""
    def __init__(self):
        self.liked_genres = set()
        self.disliked_genres = set()
        self.liked_movies = set()
        self.disliked_movies = set()
        self.min_year = None
        self.max_year = None
        self.conversation_history = []
        self.last_recommendations = []

    def update_preferences(self, movie_id=None, like=None, genre=None, 
                          genre_like=None, year_range=None):
        """Update user preferences based on interaction"""
        if movie_id is not None and like is not None:
            if like:
                self.liked_movies.add(movie_id)
                if movie_id in self.disliked_movies:
                    self.disliked_movies.remove(movie_id)
            else:
                self.disliked_movies.add(movie_id)
                if movie_id in self.liked_movies:
                    self.liked_movies.remove(movie_id)
                    
        if genre is not None and genre_like is not None:
            if genre_like:
                self.liked_genres.add(genre)
                if genre in self.disliked_genres:
                    self.disliked_genres.remove(genre)
            else:
                self.disliked_genres.add(genre)
                if genre in self.liked_genres:
                    self.liked_genres.remove(genre)
                    
        if year_range is not None:
            self.min_year, self.max_year = year_range
#class Movie Recommender
class MovieRecommender:
    """Core recommendation engine"""
    def __init__(self, movie_data):
        self.movies = movie_data
        self.genre_keywords = {
            'action': ['action', 'exciting', 'fast', 'adventure', 'explosive', 'thrill'],
            'comedy': ['comedy', 'funny', 'laugh', 'humor', 'hilarious', 'comedic'],
            'drama': ['drama', 'emotional', 'powerful', 'intense', 'serious', 'dramatic'],
            'horror': ['horror', 'scary', 'frightening', 'terror', 'creepy', 'spooky'],
            'sci-fi': ['sci-fi', 'science fiction', 'space', 'future', 'technology', 'alien'],
            'romance': ['romance', 'love', 'relationship', 'romantic', 'dating'],
            'thriller': ['thriller', 'suspense', 'tension', 'suspenseful', 'mystery'],
            'fantasy': ['fantasy', 'magical', 'supernatural', 'myth', 'dragon', 'wizard'],
            'animation': ['animation', 'animated', 'cartoon', 'pixar', 'disney'],
            'documentary': ['documentary', 'real', 'true story', 'historical', 'educational']
        }
        
        # Natural language patterns
        self.patterns = {
            'like_genre': re.compile(r'(?:i (?:like|love|enjoy|prefer))(?:[^.!?]*)(?:genre|type|category)?(?:[^.!?]*)(' + '|'.join(sum([terms for terms in self.genre_keywords.values()], [])) + ')', re.I),
            'dislike_genre': re.compile(r'(?:i (?:dislike|hate|don\'t like|do not like))(?:[^.!?]*)(?:genre|type|category)?(?:[^.!?]*)(' + '|'.join(sum([terms for terms in self.genre_keywords.values()], [])) + ')', re.I),
            'years': re.compile(r'(?:from|between|after|before)?(?:[^.!?]*)(?:year|made in|from)(?:[^.!?]*)(\d{4})(?:[^.!?]*)(?:to|and|-)(?:[^.!?]*)(\d{4})', re.I),
            'recent': re.compile(r'(?:recent|new|latest|modern|current)', re.I),
            'classic': re.compile(r'(?:classic|old|older|vintage|retro)', re.I),
            'movie_mention': re.compile(r'(?:like|love|enjoy|recommend|watch)(?:[^.!?]*)["\'](.*?)[\"\']', re.I)
        }

    def extract_preferences(self, message, context):
        """Extract preferences from user message"""
        # Extract liked genres
        like_matches = self.patterns['like_genre'].findall(message.lower())
        for match in like_matches:
            for genre, keywords in self.genre_keywords.items():
                if any(keyword in match.lower() for keyword in keywords):
                    context.update_preferences(genre=genre, genre_like=True)

        # Extract disliked genres
        dislike_matches = self.patterns['dislike_genre'].findall(message.lower())
        for match in dislike_matches:
            for genre, keywords in self.genre_keywords.items():
                if any(keyword in match.lower() for keyword in keywords):
                    context.update_preferences(genre=genre, genre_like=False)

        # Extract year preferences
        year_matches = self.patterns['years'].findall(message)
        if year_matches:
            try:
                min_year, max_year = sorted([int(y) for y in year_matches[0]])
                context.update_preferences(year_range=(min_year, max_year))
            except (ValueError, IndexError):
                pass

        # Check for recent movies preference
        if self.patterns['recent'].search(message):
            context.update_preferences(year_range=(2015, 2025))

        # Check for classic movies preference
        if self.patterns['classic'].search(message):
            context.update_preferences(year_range=(1950, 1990))

        # Extract mentioned movies
        movie_matches = self.patterns['movie_mention'].findall(message)
        for movie_name in movie_matches:
            # Try to find the movie in our database
            possible_matches = self.movies[self.movies['title'].str.contains(movie_name, case=False)]
            if not possible_matches.empty:
                context.update_preferences(movie_id=possible_matches.iloc[0]['movie_id'], like=True)

    def get_recommendations(self, context, num_recommendations=5):
        """Generate movie recommendations based on user context"""
        if not context.liked_genres and not context.liked_movies:
            # Cold start - recommend popular movies
            recommendations = self.movies.sort_values('popularity', ascending=False).head(num_recommendations)
            return recommendations.to_dict('records')
        
        # Calculate scores based on preferences
        scores = []
        
        for _, movie in self.movies.iterrows():
            score = 0
            
            # Genre matching
            movie_genres = str(movie['genres']).lower().split('|')
            for genre in context.liked_genres:
                if genre in movie_genres:
                    score += 2
            for genre in context.disliked_genres:
                if genre in movie_genres:
                    score -= 3
            
            # Year matching
            if context.min_year and context.max_year:
                year = movie['year']
                if context.min_year <= year <= context.max_year:
                    score += 1
                else:
                    score -= 0.5
            
            # Similar to liked movies
            for liked_id in context.liked_movies:
                if movie['movie_id'] == liked_id:
                    continue  # Don't recommend the same movie
                
                liked_movie = self.movies[self.movies['movie_id'] == liked_id]
                if not liked_movie.empty:
                    liked_genres = str(liked_movie.iloc[0]['genres']).lower().split('|')
                    common_genres = set(movie_genres).intersection(set(liked_genres))
                    score += len(common_genres) * 0.5
            
            # Penalize disliked movies
            if movie['movie_id'] in context.disliked_movies:
                score -= 10
                
            # Penalize previously recommended movies
            if movie['movie_id'] in context.last_recommendations:
                score -= 5
                
            scores.append((movie['movie_id'], score))
        
        # Sort by score and get top recommendations
        scores.sort(key=lambda x: x[1], reverse=True)
        top_movie_ids = [movie_id for movie_id, _ in scores[:num_recommendations]]
        
        # Get the full movie records
        recommendations = self.movies[self.movies['movie_id'].isin(top_movie_ids)]
        
        # Update last recommendations
        context.last_recommendations = top_movie_ids
        
        return recommendations.to_dict('records')

    def generate_response(self, message, context, recommendations):
        """Generate natural language response"""
        # Add basic greeting if it's the first message
        if not context.conversation_history:
            response = "Hello! I'm your movie recommendation assistant. "
        else:
            response = ""

        #Add Referenece acknowledgement
        if any(term in message.lower() for term in ['hi', 'hello', 'hey', 'start']):
            response += "How can I help you find a movie today? Tell me what kinds of movies you enjoy."
            return response
        
        if context.liked_genres:
            genres_text = ", ".join(list(context.liked_genres)[:-1]) + " and " + list(context.liked_genres)[-1] if len(context.liked_genres) > 1 else list(context.liked_genres)[0]
            response += f"Based on your interest in {genres_text}, "
        
        if context.min_year and context.max_year:
            response += f"and your preference for movies from {context.min_year} to {context.max_year}, "
        
        # Add recommendation text
        if recommendations:
            response += "I recommend these movies:\n\n"
            for i, movie in enumerate(recommendations[:5], 1):
                response += f"{i}. {movie['title']} ({movie['year']}) - {movie['genres']}\n"
        else:
            response += "I don't have specific recommendations yet. Could you tell me more about what movies you enjoy?"
        
        # Add follow-up question
        if len(context.conversation_history) < 3:
            response += "\n\nIs there a specific genre or time period you're interested in?"
        else:
            response += "\n\nWhat do you think of these recommendations? Or would you like to explore something different?"
        
        return response
    # function for process message
    def process_message(self, message, context):
        """Process user message and return response with recommendations"""
        # Update conversation history
        context.conversation_history.append(message)
        
        # Extract preferences from message
        self.extract_preferences(message, context)
        
        # Generate recommendations
        recommendations = self.get_recommendations(context)
        
        # Generate response
        response = self.generate_response(message, context, recommendations)
        
        return response, recommendations
#function for creating sample dataset
def create_sample_dataset():
    """Create a sample movie dataset if none exists"""
    data = {
        'movie_id': list(range(1, 51)),
        'title': [
            "The Shawshank Redemption", "The Godfather", "Pulp Fiction", "The Dark Knight", "Schindler's List",
            "Forrest Gump", "The Matrix", "Goodfellas", "Inception", "The Silence of the Lambs",
            "Interstellar", "The Lord of the Rings: The Fellowship of the Ring", "Star Wars: Episode V - The Empire Strikes Back",
            "The Green Mile", "The Avengers", "Jurassic Park", "Titanic", "Avatar", "The Lion King", "Gladiator",
            "E.T. the Extra-Terrestrial", "Back to the Future", "Raiders of the Lost Ark", "The Shining", "Alien",
            "Finding Nemo", "WALL-E", "Up", "Toy Story", "Inside Out",
            "The Grand Budapest Hotel", "La La Land", "Moonlight", "Parasite", "Get Out",
            "Jaws", "Halloween", "The Exorcist", "A Nightmare on Elm Street", "The Conjuring",
            "When Harry Met Sally", "The Notebook", "Pride and Prejudice", "Eternal Sunshine of the Spotless Mind", "Casablanca",
            "March of the Penguins", "Planet Earth", "Free Solo", "Amy", "Won't You Be My Neighbor?"
        ],
        'year': [
            1994, 1972, 1994, 2008, 1993,
            1994, 1999, 1990, 2010, 1991,
            2014, 2001, 1980, 1999, 2012,
            1993, 1997, 2009, 1994, 2000,
            1982, 1985, 1981, 1980, 1979,
            2003, 2008, 2009, 1995, 2015,
            2014, 2016, 2016, 2019, 2017,
            1975, 1978, 1973, 1984, 2013,
            1989, 2004, 2005, 2004, 1942,
            2005, 2006, 2018, 2015, 2018
        ],
        'genres': [
            "drama", "drama|crime", "crime|drama", "action|crime|drama", "biography|drama|history",
            "drama|romance", "action|sci-fi", "biography|crime|drama", "action|adventure|sci-fi", "crime|drama|thriller",
            "adventure|drama|sci-fi", "adventure|drama|fantasy", "action|adventure|fantasy", "crime|drama|fantasy", "action|adventure|sci-fi",
            "adventure|sci-fi|thriller", "drama|romance", "action|adventure|fantasy", "animation|adventure|drama", "action|adventure|drama",
            "adventure|family|sci-fi", "adventure|comedy|sci-fi", "action|adventure", "drama|horror", "horror|sci-fi",
            "animation|adventure|comedy", "animation|adventure|family", "animation|adventure|comedy", "animation|adventure|comedy", "animation|adventure|comedy",
            "adventure|comedy|drama", "comedy|drama|music", "drama", "comedy|drama|thriller", "horror|mystery|thriller",
            "adventure|drama|thriller", "horror|thriller", "horror", "horror", "horror|mystery|thriller",
            "comedy|romance", "drama|romance", "drama|romance", "drama|romance|sci-fi", "drama|romance|war",
            "documentary", "documentary", "documentary|sport", "documentary|biography|music", "documentary|biography"
        ],
        'popularity': [
            9.3, 9.2, 8.9, 9.0, 8.9,
            8.8, 8.7, 8.7, 8.8, 8.6,
            8.6, 8.8, 8.7, 8.6, 8.0,
            8.1, 7.8, 7.8, 8.5, 8.5,
            7.8, 8.5, 8.4, 8.4, 8.4,
            8.1, 8.4, 8.2, 8.3, 8.2,
            8.1, 8.0, 7.4, 8.6, 7.7,
            8.0, 7.8, 8.0, 7.5, 7.5,
            7.6, 7.8, 7.8, 8.3, 8.5,
            7.6, 9.4, 8.2, 7.8, 8.4
        ]
    }
    
    df = pd.DataFrame(data)
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/movies.csv', index=False)
    
    return df