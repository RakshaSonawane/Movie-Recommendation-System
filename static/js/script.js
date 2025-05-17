document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const chatHistory = document.getElementById('chat-history');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const resetButton = document.getElementById('reset-button');
    const recommendationsContainer = document.getElementById('movie-recommendations');
    
    // Generate a random user ID (in a real app, use proper authentication)
    const userId = 'user_' + Math.random().toString(36).substring(2, 15);
    // Function to add message to chat history
    function addMessage(message, type) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${type}`;
        
        // Process newlines in the message
        const formattedMessage = message.replace(/\n/g, '<br>');
        messageElement.innerHTML = formattedMessage;
        
        chatHistory.appendChild(messageElement);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }
    
    // Function to display movie recommendations
    function displayRecommendations(recommendations) {
        if (!recommendations || recommendations.length === 0) {
            recommendationsContainer.innerHTML = '<p>No recommendations available yet. Tell me more about your preferences!</p>';
            return;
        }
        
        recommendationsContainer.innerHTML = '';
        
        recommendations.forEach(movie => {
            const movieCard = document.createElement('div');
            movieCard.className = 'movie-card';
            
            const title = document.createElement('div');
            title.className = 'movie-title';
            title.textContent = movie.title;
            
            const year = document.createElement('div');
            year.className = 'movie-year';
            year.textContent = `Year: ${movie.year}`;
            
            const genres = document.createElement('div');
            genres.className = 'movie-genres';
            genres.textContent = `Genres: ${movie.genres}`;
            
            movieCard.appendChild(title);
            movieCard.appendChild(year);
            movieCard.appendChild(genres);
            
            // Add click event to add movie to chat
            movieCard.addEventListener('click', function() {
                userInput.value = `I like "${movie.title}"`;
                sendButton.click();
            });
            
            recommendationsContainer.appendChild(movieCard);
        });
    }
    

    });