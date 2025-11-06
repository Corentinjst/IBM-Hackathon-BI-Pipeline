<template>
  <div class="chatbot-container">
    <div class="chat-header">
      <h2>💬 Assistant IA</h2>
    </div>

    <div class="chat-messages" ref="messagesContainer">
      <div class="messages-inner">
        <!-- Suggestions de questions populaires -->
        <div v-if="messages.length === 0 && popularQuestions.length > 0" class="popular-questions">
          <h3>💡 Questions fréquentes</h3>
          <div class="questions-grid">
            <button
              v-for="(question, index) in popularQuestions"
              :key="index"
              @click="askQuestion(question)"
              class="question-card"
            >
              {{ question }}
            </button>
          </div>
        </div>

        <!-- Messages -->
        <div
          v-for="(message, index) in messages"
          :key="index"
          :class="['message', message.type]"
        >
          <div class="message-content">
            <div v-if="message.type === 'user'" class="text">
              {{ message.text }}
            </div>
            <div v-else-if="message.type === 'assistant'" class="assistant-message">
              <div v-html="message.html" class="html-content"></div>
              <div v-if="message.duration" class="duration">
                ⏱️ Réponse en {{ message.duration }}s
              </div>
              <div v-if="!message.feedback" class="feedback-buttons">
                <button
                  @click="sendFeedback(index, 'up')"
                  class="feedback-btn thumbs-up"
                  title="Pouce bleu"
                >
                  👍
                </button>
                <button
                  @click="sendFeedback(index, 'down')"
                  class="feedback-btn thumbs-down"
                  title="Pouce rouge"
                >
                  👎
                </button>
              </div>
              <div v-else class="feedback-sent">
                Merci pour votre retour ! {{ message.feedback === 'up' ? '👍' : '👎' }}
              </div>
            </div>
            <div v-else-if="message.type === 'loading'" class="loading">
              <div class="spinner"></div>
              <div class="timer">⏱️ {{ timer }}s</div>
              <div class="loading-text">L'assistant réfléchit...</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="chat-input-wrapper">
      <div class="chat-input">
        <input
          v-model="userInput"
          @keyup.enter="sendMessage"
          :disabled="isLoading"
          placeholder="Posez votre question..."
          type="text"
        />
        <button @click="sendMessage" :disabled="isLoading || !userInput.trim()">
          {{ isLoading ? '⏳' : '➤' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue';

// Configuration des URLs d'API
const CHAT_API_URL = 'http://127.0.0.1:8000/ask'; 
const FEEDBACK_API_URL = 'http://localhost:3000/api/dashboard/feedback'; // URL pour le feedback
const POPULAR_QUESTIONS_API_URL = 'http://localhost:3000/api/dashboard/questions'; // URL pour les questions populaires

// État réactif
const messages = ref([]);
const userInput = ref('');
const isLoading = ref(false);
const timer = ref(0);
const messagesContainer = ref(null);
const popularQuestions = ref([]);
let timerInterval = null;

// Fonction pour récupérer les questions populaires
const fetchPopularQuestions = async () => {
  try {
    const response = await fetch(POPULAR_QUESTIONS_API_URL);
    
    if (!response.ok) {
      throw new Error('Erreur lors de la récupération des questions populaires');
    }

    const data = await response.json();
    
    // Extraire les titres des questions et limiter à 3 questions maximum
    popularQuestions.value = data.slice(0, 3).map(item => item.matched_question_title);
  } catch (error) {
    console.error('Erreur lors du chargement des questions populaires:', error);
    // Garder un tableau vide en cas d'erreur
    popularQuestions.value = [];
  }
};

// Fonction pour poser une question depuis les suggestions
const askQuestion = (question) => {
  userInput.value = question;
  sendMessage();
};

// Fonction pour faire défiler vers le bas
const scrollToBottom = async () => {
  await nextTick();
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
};

// Fonction pour démarrer le chronomètre
const startTimer = () => {
  timer.value = 0;
  timerInterval = setInterval(() => {
    timer.value += 0.1;
    timer.value = Math.round(timer.value * 10) / 10;
  }, 100);
};

// Fonction pour arrêter le chronomètre
const stopTimer = () => {
  if (timerInterval) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
  return timer.value;
};

// Fonction pour envoyer un message
const sendMessage = async () => {
  if (!userInput.value.trim() || isLoading.value) return;

  const userMessage = userInput.value.trim();
  userInput.value = '';

  // Ajouter le message de l'utilisateur
  messages.value.push({
    type: 'user',
    text: userMessage,
  });
  scrollToBottom();

  // Ajouter l'indicateur de chargement
  isLoading.value = true;
  messages.value.push({
    type: 'loading',
  });
  scrollToBottom();

  // Démarrer le chronomètre
  startTimer();

  try {
    // Appel API
    const response = await fetch(CHAT_API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: userMessage,
      }),
    });

    if (!response.ok) {
      throw new Error('Erreur lors de l\'appel API');
    }

    const data = await response.json();
    
    // Arrêter le chronomètre
    const duration = stopTimer();

    // Retirer l'indicateur de chargement
    messages.value.pop();

    // ✅ Vérifier que matches existe et n'est pas vide
    if (!data.matches || data.matches.length === 0) {
      messages.value.push({
        type: 'assistant',
        html: '<p style="color: #e74c3c;">❌ Aucune réponse trouvée pour votre question.</p>',
        duration: duration,
        feedback: null,
        userQuery: userMessage,
        matchedQuestionId: null,
        matchedQuestionTitle: null,
        similarityScore: null,
        responseTimeMs: Math.round(duration * 1000),
      });
      scrollToBottom();
      return;
    }
    
    // ✅ Récupérer le premier match
    const firstMatch = data.matches[0];

    // Ajouter la réponse de l'assistant
    messages.value.push({
      type: 'assistant',
      html: firstMatch.answer || '<p>Réponse non disponible</p>', // ✅ Utiliser 'answer'
      duration: duration,
      feedback: null,
      // Données pour le feedback
      userQuery: userMessage,
      matchedQuestionId: firstMatch.id,
      matchedQuestionTitle: firstMatch.question,
      similarityScore: firstMatch.score,
      responseTimeMs: Math.round(duration * 1000),
    });

    scrollToBottom();
  } catch (error) {
    console.error('Erreur:', error);
    
    // Arrêter le chronomètre
    stopTimer();

    // Retirer l'indicateur de chargement
    messages.value.pop();

    // Afficher un message d'erreur
    messages.value.push({
      type: 'assistant',
      html: '<p style="color: #e74c3c;">❌ Désolé, une erreur s\'est produite. Veuillez réessayer.</p>',
      duration: null,
      feedback: null,
      userQuery: userMessage,
      matchedQuestionId: null,
      matchedQuestionTitle: null,
      similarityScore: null,
      responseTimeMs: null,
    });

    scrollToBottom();
  } finally {
    isLoading.value = false;
  }
};

// Fonction pour envoyer le feedback
const sendFeedback = async (messageIndex, feedbackType) => {
  const message = messages.value[messageIndex];
  
  if (message.feedback) return; // Déjà envoyé

  try {
    // Appel API de feedback avec toutes les données nécessaires
    await fetch(FEEDBACK_API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_query: message.userQuery, // Question de l'utilisateur
        matched_question_id: message.matchedQuestionId, // ID de la question matchée
        matched_question_title: message.matchedQuestionTitle, // Titre de la question matchée
        similarity_score: message.similarityScore, // Score de similarité
        was_helpful: feedbackType === 'up' ? true : false, // true pour 👍, false pour 👎
        user_feedback: null, // Pour commentaires futurs (actuellement null)
        response_time_ms: message.responseTimeMs, // Temps de réponse en millisecondes
        // timestamp est géré automatiquement par la base de données (CURRENT_TIMESTAMP)
      }),
    });

    // Mettre à jour le message avec le feedback
    message.feedback = feedbackType;
  } catch (error) {
    console.error('Erreur lors de l\'envoi du feedback:', error);
    // On peut quand même afficher le feedback localement même si l'envoi échoue
    message.feedback = feedbackType;
  }
};

// Charger les questions populaires au montage du composant
onMounted(() => {
  fetchPopularQuestions();
});
</script>

<style scoped>
.chatbot-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100%;
  background: #f8f9fa;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.chat-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 16px 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.chat-header h2 {
  margin: 0;
  font-size: 1.4rem;
  font-weight: 600;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  background: #f8f9fa;
}

.messages-inner {
  max-width: 900px;
  margin: 0 auto;
  padding: 32px 24px;
}

/* Styles pour les questions populaires */
.popular-questions {
  margin-bottom: 40px;
  animation: fadeIn 0.5s ease-in;
}

.popular-questions h3 {
  color: #2c3e50;
  font-size: 1.3rem;
  margin-bottom: 20px;
  font-weight: 600;
}

.questions-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.question-card {
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  padding: 16px 20px;
  text-align: left;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1rem;
  color: #2c3e50;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.question-card:hover {
  border-color: #667eea;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
}

.question-card:active {
  transform: translateY(0);
}

.message {
  margin-bottom: 24px;
  display: flex;
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message.user {
  justify-content: flex-end;
}

.message.assistant {
  justify-content: flex-start;
}

.message-content {
  max-width: 75%;
  padding: 16px 20px;
  border-radius: 16px;
  word-wrap: break-word;
}

.message.user .message-content {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.message.assistant .message-content {
  background: white;
  color: #2c3e50;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.message.loading .message-content {
  background: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.text {
  line-height: 1.6;
  font-size: 1rem;
}

.html-content {
  line-height: 1.7;
  font-size: 1rem;
}

.html-content :deep(p) {
  margin: 0 0 12px 0;
}

.html-content :deep(p:last-child) {
  margin-bottom: 0;
}

.html-content :deep(ul),
.html-content :deep(ol) {
  margin: 12px 0;
  padding-left: 24px;
}

.html-content :deep(li) {
  margin: 6px 0;
}

.html-content :deep(code) {
  background: #f4f4f4;
  padding: 2px 8px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
}

.html-content :deep(pre) {
  background: #2d2d2d;
  color: #f8f8f2;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 12px 0;
}

.duration {
  margin-top: 10px;
  font-size: 0.85rem;
  color: #7f8c8d;
  font-style: italic;
}

.feedback-buttons {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #ecf0f1;
}

.feedback-btn {
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  padding: 6px 14px;
  cursor: pointer;
  font-size: 1.1rem;
  transition: all 0.2s ease;
}

.feedback-btn:hover {
  transform: scale(1.05);
}

.feedback-btn.thumbs-up:hover {
  border-color: #3498db;
  background: #ebf5fb;
}

.feedback-btn.thumbs-down:hover {
  border-color: #e74c3c;
  background: #fadbd8;
}

.feedback-sent {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #ecf0f1;
  color: #27ae60;
  font-size: 0.9rem;
  font-weight: 500;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.timer {
  font-size: 1.1rem;
  font-weight: 600;
  color: #667eea;
}

.loading-text {
  color: #7f8c8d;
  font-size: 0.95rem;
}

.chat-input-wrapper {
  background: white;
  border-top: 1px solid #e0e0e0;
  padding: 20px 24px 24px;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.05);
}

.chat-input {
  max-width: 900px;
  margin: 0 auto;
  display: flex;
  gap: 12px;
}

.chat-input input {
  flex: 1;
  padding: 14px 20px;
  border: 2px solid #e0e0e0;
  border-radius: 28px;
  font-size: 1rem;
  outline: none;
  transition: all 0.3s ease;
  background: white;
}

.chat-input input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.chat-input input:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
  color: #95a5a6;
}

.chat-input button {
  padding: 14px 28px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 28px;
  font-size: 1.2rem;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.chat-input button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.chat-input button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* Scrollbar personnalisée */
.chat-messages::-webkit-scrollbar {
  width: 10px;
}

.chat-messages::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: #cbd5e0;
  border-radius: 5px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: #a0aec0;
}

/* Responsive */
@media (max-width: 768px) {
  .messages-inner {
    padding: 20px 16px;
  }

  .message-content {
    max-width: 85%;
  }

  .popular-questions h3 {
    font-size: 1.1rem;
  }

  .question-card {
    padding: 14px 16px;
    font-size: 0.95rem;
  }

  .chat-input-wrapper {
    padding: 16px;
  }

  .chat-input {
    gap: 8px;
  }

  .chat-input input {
    padding: 12px 16px;
    font-size: 0.95rem;
  }

  .chat-input button {
    padding: 12px 20px;
  }
}
</style>