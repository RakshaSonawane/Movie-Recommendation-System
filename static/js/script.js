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
        // Function to send message to server
    async function sendMessage(message) {
        try {
            // Display user message
            addMessage(message, 'user');
            
            // Clear input field
            userInput.value = '';
            
            // Add loading indicator
            const loadingElement = document.createElement('div');
            loadingElement.className = 'message assistant';
            loadingElement.textContent = 'Thinking...';
            chatHistory.appendChild(loadingElement);
            
            // Send message to server
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_id: userId,
                    message: message
                })
            });
            
            // Process response
            const data = await response.json();
            
            // Remove loading indicator
            chatHistory.removeChild(loadingElement);
            
            // Display assistant message
            addMessage(data.response, 'assistant');
            
            // Update recommendations
            displayRecommendations(data.recommendations);
            
        } catch (error) {
            console.error('Error sending message:', error);
            addMessage('Sorry, there was an error processing your request. Please try again.', 'system');
        }
    }
    
    // Function to reset user preferences
    async function resetPreferences() {
        try {
            const response = await fetch('/reset', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_id: userId
                })
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                addMessage('I\'ve reset your preferences. Let\'s start fresh! What kind of movies do you like?', 'system');
                recommendationsContainer.innerHTML = '<p>Your recommendations will appear here once we chat about your preferences.</p>';
            }
            
        } catch (error) {
            console.error('Error resetting preferences:', error);
            addMessage('Sorry, there was an error resetting your preferences. Please try again.', 'system');
        }
    }
    
    // Event listeners
    sendButton.addEventListener('click', function() {
        const message = userInput.value.trim();
        if (message) {
            sendMessage(message);
        }
    });
    // Adding another event listener
    userInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            const message = userInput.value.trim();
            if (message) {
                sendMessage(message);
            }
        }
    });
    
    resetButton.addEventListener('click', resetPreferences);
    
    // Focus input field on page load
    userInput.focus();


    });