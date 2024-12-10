const messageContainer = document.getElementById('messageContainer');
const userInput = document.getElementById('userInput');
const sendButton = document.getElementById('sendButton');
const micButton = document.getElementById('micButton');
const collegeSelect = document.getElementById('collegeSelect');

let selectedCollege = null;

// Initial bot message
const initialMessage = {
  text: "Hello! How can I assist you today? Please select your college.",
  isBot: true,
};
displayMessage(initialMessage.text, 'bot');

// Event listener for college selection
collegeSelect.addEventListener('change', () => {
  selectedCollege = collegeSelect.value;
  if (selectedCollege) {
    displayMessage(`You selected: ${selectedCollege.replace(/_/g, ' ')}`, 'bot');
  }
});

// Event listener for send button
sendButton.addEventListener('click', handleUserInput);

// Event listener for pressing Enter key in the input field
userInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') handleUserInput();
});

function handleUserInput() {
  const text = userInput.value.trim();
  if (!text) return;
  if (!selectedCollege) {
    displayMessage("Please select a college before sending a message.", 'bot');
    return;
  }

  displayMessage(text, 'user');
  const messageToSend = text;
  userInput.value = '';
  simulateBotResponse(messageToSend);
}

function displayMessage(text, type) {
  const messageElement = document.createElement('div');
  messageElement.className = `message ${type}`;
  messageElement.textContent = text;
  messageContainer.appendChild(messageElement);
  messageContainer.scrollTop = messageContainer.scrollHeight;
}

function simulateBotResponse(messageToSend) {
  const loadingMessage = document.createElement('div');
  loadingMessage.className = 'message bot';
  loadingMessage.textContent = 'Assistant is thinking...';
  messageContainer.appendChild(loadingMessage);
  messageContainer.scrollTop = messageContainer.scrollHeight;

  setTimeout(() => {
    loadingMessage.remove();
    fetchBotResponse(messageToSend);
  }, 1500);
}

function fetchBotResponse(userMessage) {
  fetch('/get_response', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message: userMessage, college: selectedCollege })
  })
  .then(response => response.json())
  .then(data => {
    displayMessage(data.response, 'bot');
  })
  .catch(error => {
    console.error('Error fetching response:', error);
    displayMessage('An error occurred while fetching the response. Please try again.', 'bot');
  });
}