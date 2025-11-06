<template>
  <div class="chatbot-container">
    <!-- Support Form Modal -->
    <transition name="modal-fade">
      <div v-if="showSupportForm" class="modal-overlay" @click="closeSupportForm">
        <div class="modal-container support-form-modal" @click.stop>
          <SupportForm
            :initialQuestion="currentUserQuery"
            @cancel="closeSupportForm"
            @success="handleSupportFormSuccess"
          />
        </div>
      </div>
    </transition>

    <!-- Header with Glassmorphism -->
    <div class="chat-header">
      <div class="header-content">
        <div class="header-icon">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM12 20C7.59 20 4 16.41 4 12C4 7.59 7.59 4 12 4C16.41 4 20 7.59 20 12C20 16.41 16.41 20 12 20Z" fill="currentColor" fill-opacity="0.3"/>
            <path d="M13 7H11V13H17V11H13V7Z" fill="currentColor"/>
            <circle cx="12" cy="12" r="2" fill="currentColor"/>
          </svg>
        </div>
        <div class="header-text">
          <h2>Help Center PULV</h2>
          <p class="header-subtitle">Vous trouverez ici les réponses à toutes vos questions !</p>
        </div>

      </div>
    </div>

    <div class="chat-messages" ref="messagesContainer">
      <div class="messages-inner">
        <!-- Welcome Screen -->
        <div v-if="messages.length === 0" class="welcome-screen">
          <div class="welcome-icon">
            <div class="welcome-icon-wrapper">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M20 2H4C2.9 2 2 2.9 2 4V22L6 18H20C21.1 18 22 17.1 22 16V4C22 2.9 21.1 2 20 2Z" fill="#667eea"/>
              </svg>
            </div>
          </div>
          <h1 class="welcome-title">Bienvenue sur le Help Center du Pôle Léonard de Vinci !</h1>
          <p class="welcome-description">Posez-moi vos questions ! J'utilise la technologie RAG (Retrieval Augmented Generation) avec traitement LLM pour fournir des réponses précises.</p>

          <!-- Popular Questions -->
          <div v-if="popularQuestions.length > 0" class="popular-questions">
            <h3 class="section-title">
              <svg class="title-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" fill="currentColor"/>
              </svg>
              Questions populaires
            </h3>
            <div class="questions-grid">
              <button
                v-for="(question, index) in popularQuestions"
                :key="index"
                @click="askQuestion(question)"
                class="question-card"
              >
                <svg class="question-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM13 19H11V17H13V19ZM15.07 11.25L14.17 12.17C13.45 12.9 13 13.5 13 15H11V14.5C11 13.4 11.45 12.4 12.17 11.67L13.41 10.41C13.78 10.05 14 9.55 14 9C14 7.9 13.1 7 12 7C10.9 7 10 7.9 10 9H8C8 6.79 9.79 5 12 5C14.21 5 16 6.79 16 9C16 9.88 15.64 10.68 15.07 11.25Z" fill="currentColor"/>
                </svg>
                <span class="question-text">{{ question }}</span>
                <svg class="arrow-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M8.59 16.59L13.17 12L8.59 7.41L10 6L16 12L10 18L8.59 16.59Z" fill="currentColor"/>
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- Messages -->
        <div
          v-for="(message, index) in messages"
          :key="index"
          :class="['message', message.type]"
        >
          <!-- User Message with Avatar -->
          <div v-if="message.type === 'user'" class="message-wrapper user-message">
            <div class="message-content user-content">
              <div class="message-text">{{ message.text }}</div>
            </div>
            <div class="message-avatar user-avatar">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 12C14.21 12 16 10.21 16 8C16 5.79 14.21 4 12 4C9.79 4 8 5.79 8 8C8 10.21 9.79 12 12 12ZM12 14C9.33 14 4 15.34 4 18V20H20V18C20 15.34 14.67 14 12 14Z" fill="currentColor"/>
              </svg>
            </div>
          </div>

          <!-- Assistant Message -->
          <div v-else-if="message.type === 'assistant'" class="message-wrapper assistant-message">
            <div class="message-avatar assistant-avatar">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2Z" fill="#667eea"/>
                <circle cx="12" cy="10" r="3" fill="white"/>
                <path d="M12 14C9 14 6.5 15.5 6.5 17.5V18.5H17.5V17.5C17.5 15.5 15 14 12 14Z" fill="white"/>
              </svg>
            </div>
            <div class="message-content assistant-content">
              <div v-html="message.html" class="html-content"></div>

              <!-- Sources Section (for LLM-processed messages) -->
              <div v-if="message.sources && message.sources.length > 0" class="sources-section">
                <div class="sources-title">
                  <svg class="sources-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M14 2H6C4.9 2 4 2.9 4 4V20C4 21.1 4.9 22 6 22H18C19.1 22 20 21.1 20 20V8L14 2ZM16 18H8V16H16V18ZM16 14H8V12H16V14ZM13 9V3.5L18.5 9H13Z" fill="currentColor"/>
                  </svg>
                  <span>Sources utilisées</span>
                </div>
                <div class="sources-chips">
                  <button
                    v-for="(source, idx) in message.sources"
                    :key="idx"
                    class="source-chip"
                    @click="expandSource(source)"
                    :title="source.question"
                  >
                    <span class="chip-number">{{ idx + 1 }}</span>
                    <span class="chip-text">{{ truncateText(source.question, 40) }}</span>
                    <svg class="chip-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M19 19H5V5H12V3H5C3.89 3 3 3.9 3 5V19C3 20.1 3.89 21 5 21H19C20.1 21 21 20.1 21 19V12H19V19ZM14 3V5H17.59L7.76 14.83L9.17 16.24L19 6.41V10H21V3H14Z" fill="currentColor"/>
                    </svg>
                  </button>
                </div>
              </div>

              <!-- Metadata Footer -->
              <div class="message-footer" v-if="message.matchedQuestionId">
                <div class="metadata">
                  <span v-if="message.duration" class="duration">
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M11.99 2C6.47 2 2 6.48 2 12C2 17.52 6.47 22 11.99 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 11.99 2ZM12 20C7.58 20 4 16.42 4 12C4 7.58 7.58 4 12 4C16.42 4 20 7.58 20 12C20 16.42 16.42 20 12 20ZM12.5 7H11V13L16.25 16.15L17 14.92L12.5 12.25V7Z" fill="currentColor"/>
                    </svg>
                    {{ message.duration }}s
                  </span>
                </div>

                <!-- Feedback Buttons -->
                <div v-if="!message.feedback" class="feedback-buttons">
                  <button
                    @click="sendFeedback(index, 'up')"
                    class="feedback-btn thumbs-up"
                    title="Utile"
                  >
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M1 21H4V9H1V21ZM23 10C23 8.9 22.1 8 21 8H14.69L15.64 3.43L15.67 3.11C15.67 2.7 15.5 2.32 15.23 2.05L14.17 1L7.59 7.59C7.22 7.95 7 8.45 7 9V19C7 20.1 7.9 21 9 21H18C18.83 21 19.54 20.5 19.84 19.78L22.86 12.73C22.95 12.5 23 12.26 23 12V10Z" fill="currentColor"/>
                    </svg>
                  </button>
                  <button
                    @click="sendFeedback(index, 'down')"
                    class="feedback-btn thumbs-down"
                    title="Pas utile"
                  >
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M15 3H6C5.17 3 4.46 3.5 4.16 4.22L1.14 11.27C1.05 11.5 1 11.74 1 12V14C1 15.1 1.9 16 3 16H9.31L8.36 20.57L8.33 20.89C8.33 21.3 8.5 21.68 8.77 21.95L9.83 23L16.41 16.41C16.78 16.05 17 15.55 17 15V5C17 3.9 16.1 3 15 3ZM19 3V15H23V3H19Z" fill="currentColor"/>
                    </svg>
                  </button>
                </div>
                <div v-else class="feedback-sent">
                  <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M9 16.17L4.83 12L3.41 13.41L9 19L21 7L19.59 5.59L9 16.17Z" fill="currentColor"/>
                  </svg>
                  <span>Merci pour votre retour !</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Loading State -->
          <div v-else-if="message.type === 'loading'" class="message-wrapper assistant-message">
            <div class="message-avatar assistant-avatar">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2Z" fill="#667eea"/>
                <circle cx="12" cy="10" r="3" fill="white"/>
                <path d="M12 14C9 14 6.5 15.5 6.5 17.5V18.5H17.5V17.5C17.5 15.5 15 14 12 14Z" fill="white"/>
              </svg>
            </div>
            <div class="message-content loading-content">
              <div class="loading-animation">
                <div class="dot-pulse">
                  <div class="dot-pulse__dot"></div>
                </div>
              </div>
              <div class="loading-text">L'IA réfléchit...</div>
              <div class="timer-display">{{ timer.toFixed(1) }}s</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Source Modal -->
    <transition name="modal-fade">
      <div v-if="showSourceModal" class="modal-overlay" @click="closeModal">
        <div class="modal-container" @click.stop>
          <div class="modal-header">
            <div class="modal-title-wrapper">
              <svg class="modal-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M14 2H6C4.9 2 4 2.9 4 4V20C4 21.1 4.9 22 6 22H18C19.1 22 20 21.1 20 20V8L14 2ZM16 18H8V16H16V18ZM16 14H8V12H16V14ZM13 9V3.5L18.5 9H13Z" fill="currentColor"/>
              </svg>
              <div>
                <h3>Document source</h3>
                <p class="modal-subtitle">Contenu original de la FAQ</p>
              </div>
            </div>
            <button class="modal-close" @click="closeModal" title="Close">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M19 6.41L17.59 5L12 10.59L6.41 5L5 6.41L10.59 12L5 17.59L6.41 19L12 13.41L17.59 19L19 17.59L13.41 12L19 6.41Z" fill="currentColor"/>
              </svg>
            </button>
          </div>

          <div class="modal-body" v-if="selectedSource">
            <div class="source-meta">
              <div class="meta-item">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM13 19H11V17H13V19ZM15.07 11.25L14.17 12.17C13.45 12.9 13 13.5 13 15H11V14.5C11 13.4 11.45 12.4 12.17 11.67L13.41 10.41C13.78 10.05 14 9.55 14 9C14 7.9 13.1 7 12 7C10.9 7 10 7.9 10 9H8C8 6.79 9.79 5 12 5C14.21 5 16 6.79 16 9C16 9.88 15.64 10.68 15.07 11.25Z" fill="currentColor"/>
                </svg>
                <span class="meta-label">ID Question :</span>
                <span class="meta-value">{{ selectedSource.id }}</span>
              </div>
              <div class="meta-item" v-if="selectedSource.score">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 17.27L18.18 21L16.54 13.97L22 9.24L14.81 8.63L12 2L9.19 8.63L2 9.24L7.46 13.97L5.82 21L12 17.27Z" fill="currentColor"/>
                </svg>
                <span class="meta-label">Score de similarité :</span>
                <span class="meta-value">{{ ((selectedSource.score - 1) * 100).toFixed(1) }}%</span>
              </div>
            </div>

            <div class="source-question">
              <h4>Question</h4>
              <p>{{ selectedSource.question }}</p>
            </div>

            <div class="source-answer">
              <h4>Réponse</h4>
              <div class="answer-content" v-html="selectedSource.answer || 'Aucune réponse disponible'"></div>
            </div>
          </div>

          <div class="modal-footer">
            <button class="modal-btn modal-btn-secondary" @click="closeModal">
              Fermer
            </button>
          </div>
        </div>
      </div>
    </transition>

    <!-- Input Area -->
    <div class="chat-input-wrapper">
      <div class="chat-input-container">
        <div class="input-group">
          <input
            v-model="userInput"
            @keyup.enter="sendMessage"
            @input="handleInput"
            :disabled="isLoading"
            placeholder="Posez votre question ici..."
            type="text"
            class="chat-input"
          />
          <button
            @click="sendMessage"
            :disabled="isLoading || !userInput.trim()"
            class="send-btn"
            :class="{ active: userInput.trim() }"
          >
            <svg v-if="!isLoading" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M2.01 21L23 12L2.01 3L2 10L17 12L2 14L2.01 21Z" fill="currentColor"/>
            </svg>
            <svg v-else class="loading-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 4V2C12 2 12 2 12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 9.24 20.88 6.74 19.05 5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </button>
        </div>
        <div class="input-hint">Appuyez sur Entrée pour envoyer</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue';
import SupportForm from './SupportForm.vue';

// Configuration des URLs d'API
const CHAT_API_URL = 'http://127.0.0.1:8000/ask';
const FEEDBACK_API_URL = 'http://localhost:3000/api/dashboard/feedback';
const POPULAR_QUESTIONS_API_URL = 'http://localhost:3000/api/dashboard/questions';

// État réactif
const messages = ref([]);
const userInput = ref('');
const isLoading = ref(false);
const timer = ref(0);
const messagesContainer = ref(null);
const popularQuestions = ref([]);
const showSourceModal = ref(false);
const selectedSource = ref(null);
const showSupportForm = ref(false);
const currentUserQuery = ref('');
let timerInterval = null;

// Fonction pour récupérer les questions populaires
const fetchPopularQuestions = async () => {
  try {
    const response = await fetch(POPULAR_QUESTIONS_API_URL);

    if (!response.ok) {
      throw new Error('Erreur lors de la récupération des questions populaires');
    }

    const data = await response.json();
    popularQuestions.value = data.slice(0, 3).map(item => item.matched_question_title);
  } catch (error) {
    console.error('Erreur lors du chargement des questions populaires:', error);
    popularQuestions.value = [];
  }
};

// Fonction pour poser une question depuis les suggestions
const askQuestion = (question) => {
  userInput.value = question;
  sendMessage();
};

// Fonction pour gérer l'input
const handleInput = () => {
  // Add any input handling logic here
};

// Helper function to truncate text
const truncateText = (text, maxLength) => {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

// Function to expand/show source details in modal
const expandSource = async (source) => {
  console.log('Source clicked:', source);

  // If we have the answer already in the source, use it
  if (source.answer) {
    selectedSource.value = source;
    showSourceModal.value = true;
    return;
  }

  // Otherwise, we need to fetch it from the raw_matches or backend
  // For now, we'll use what we have
  selectedSource.value = {
    ...source,
    answer: source.answer || '<p>Answer content not available in current response format.</p>'
  };
  showSourceModal.value = true;
};

// Function to close modal
const closeModal = () => {
  showSourceModal.value = false;
  setTimeout(() => {
    selectedSource.value = null;
  }, 300); // Wait for animation to complete
};

// Function to open support form
const openSupportForm = (query) => {
  currentUserQuery.value = query;
  showSupportForm.value = true;
};

// Function to close support form
const closeSupportForm = () => {
  showSupportForm.value = false;
  setTimeout(() => {
    currentUserQuery.value = '';
  }, 300);
};

// Function to handle support form success
const handleSupportFormSuccess = () => {
  closeSupportForm();
  // Optionally add a success message to the chat
  messages.value.push({
    type: 'assistant',
    html: '<p style="color: #10b981;">✅ Votre ticket de support a été créé avec succès ! Nous vous contacterons prochainement.</p>',
    duration: null,
    feedback: null,
  });
  scrollToBottom();
};

// Fonction pour faire défiler vers le bas
const scrollToBottom = async () => {
  await nextTick();
  if (messagesContainer.value) {
    messagesContainer.value.scrollTo({
      top: messagesContainer.value.scrollHeight,
      behavior: 'smooth'
    });
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
    const duration = stopTimer();
    messages.value.pop();

    console.log('Received data:', data); // Debug log

    // ✅ NEW SCHEMA: Check for answer_html (new format from backend)
    if (data.answer_html !== undefined) {
      // New JSON schema format from backend
      const answered = data.answered !== false;

      if (!answered || !data.answer_html) {
        messages.value.push({
          type: 'assistant',
          html: data.answer_html || '<p style="color: #ef4444;">❌ Aucune réponse satisfaisante trouvée pour votre question.</p>',
          duration: duration,
          feedback: null,
          userQuery: userMessage,
          matchedQuestionId: null,
          matchedQuestionTitle: null,
          similarityScore: null,
          responseTimeMs: Math.round(duration * 1000),
          noAnswerFound: true,
        });
        scrollToBottom();
        // Ouvrir automatiquement le formulaire de support
        openSupportForm(userMessage);
        return;
      }

      // Extract sources from citations
      const sources = data.citations ? data.citations.map(cite => ({
        id: cite.id,
        question: cite.title,
        score: null, // Score not provided in new schema
        url: cite.url
      })) : [];

      const primarySource = sources.length > 0 ? sources[0] : null;

      messages.value.push({
        type: 'assistant',
        html: data.answer_html,
        duration: duration,
        feedback: null,
        userQuery: userMessage,
        matchedQuestionId: primarySource?.id || (data.used_source_ids?.[0] || null),
        matchedQuestionTitle: primarySource?.question || 'LLM Synthesized',
        similarityScore: null,
        responseTimeMs: Math.round(duration * 1000),
        llmProcessed: true,
        sources: sources,
        showSources: false,
        redirect: data.redirect,
        language: data.language
      });
    }
    // OLD SCHEMA: Legacy format support (if backend returns old format)
    else if (data.llm_processed) {
      if (!data.answer) {
        messages.value.push({
          type: 'assistant',
          html: '<p style="color: #ef4444;">❌ Aucune réponse satisfaisante trouvée pour votre question.</p>',
          duration: duration,
          feedback: null,
          userQuery: userMessage,
          matchedQuestionId: null,
          matchedQuestionTitle: null,
          similarityScore: null,
          responseTimeMs: Math.round(duration * 1000),
          noAnswerFound: true,
        });
        scrollToBottom();
        openSupportForm(userMessage);
        return;
      }

      const primarySource = data.sources && data.sources.length > 0 ? data.sources[0] : null;

      messages.value.push({
        type: 'assistant',
        html: data.answer,
        duration: duration,
        feedback: null,
        userQuery: userMessage,
        matchedQuestionId: primarySource?.id || null,
        matchedQuestionTitle: primarySource?.question || 'LLM Synthesized',
        similarityScore: primarySource?.score || null,
        responseTimeMs: Math.round(duration * 1000),
        llmProcessed: true,
        sources: data.sources,
        showSources: false,
      });
    }
    // RAW MATCHES: No LLM processing
    else if (data.matches) {
      if (data.matches.length === 0) {
        messages.value.push({
          type: 'assistant',
          html: '<p style="color: #ef4444;">❌ Aucune réponse satisfaisante trouvée pour votre question.</p>',
          duration: duration,
          feedback: null,
          userQuery: userMessage,
          matchedQuestionId: null,
          matchedQuestionTitle: null,
          similarityScore: null,
          responseTimeMs: Math.round(duration * 1000),
          noAnswerFound: true,
        });
        scrollToBottom();
        openSupportForm(userMessage);
        return;
      }

      const firstMatch = data.matches[0];

      messages.value.push({
        type: 'assistant',
        html: firstMatch.answer || '<p>Answer not available</p>',
        duration: duration,
        feedback: null,
        userQuery: userMessage,
        matchedQuestionId: firstMatch.id,
        matchedQuestionTitle: firstMatch.question,
        similarityScore: firstMatch.score,
        responseTimeMs: Math.round(duration * 1000),
        llmProcessed: false,
      });
    }
    // Unknown format
    else {
      messages.value.push({
        type: 'assistant',
        html: '<p style="color: #ef4444;">❌ Unexpected response format from server.</p>',
        duration: duration,
        feedback: null,
        userQuery: userMessage,
        matchedQuestionId: null,
        matchedQuestionTitle: null,
        similarityScore: null,
        responseTimeMs: Math.round(duration * 1000),
      });
    }

    scrollToBottom();
  } catch (error) {
    console.error('Erreur:', error);
    stopTimer();
    messages.value.pop();

    messages.value.push({
      type: 'assistant',
      html: '<p style="color: #ef4444;">❌ Sorry, an error occurred. Please try again.</p>',
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

  if (message.feedback) return;

  try {
    await fetch(FEEDBACK_API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_query: message.userQuery,
        matched_question_id: message.matchedQuestionId,
        matched_question_title: message.matchedQuestionTitle,
        similarity_score: message.similarityScore,
        was_helpful: feedbackType === 'up' ? true : false,
        user_feedback: null,
        response_time_ms: message.responseTimeMs,
      }),
    });

    message.feedback = feedbackType;
  } catch (error) {
    console.error('Erreur lors de l\'envoi du feedback:', error);
    message.feedback = feedbackType;
  }
};

// Charger les questions populaires au montage du composant
onMounted(() => {
  fetchPopularQuestions();
});
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.chatbot-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100%;
  background: #f5f7fa;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
  position: relative;
  overflow: hidden;
}

/* Animated Background Pattern */
.chatbot-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image:
    radial-gradient(circle at 20% 50%, rgba(102, 126, 234, 0.05) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(118, 75, 162, 0.05) 0%, transparent 50%);
  pointer-events: none;
  animation: backgroundShift 20s ease infinite;
}

@keyframes backgroundShift {
  0%, 100% { opacity: 1; transform: translateY(0); }
  50% { opacity: 0.8; transform: translateY(-10px); }
}

/* ============================================
   HEADER
============================================ */
.chat-header {
  background: #667eea;
  padding: 20px 28px;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
  backdrop-filter: blur(10px);
  z-index: 100;
  position: relative;
}

.header-content {
  max-width: 1000px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-icon {
  width: 48px;
  height: 48px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.header-icon svg {
  width: 28px;
  height: 28px;
  color: white;
}

.header-text {
  flex: 1;
}

.header-text h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
  letter-spacing: -0.5px;
}

.header-subtitle {
  margin: 2px 0 0 0;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.85);
  font-weight: 500;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.2);
  padding: 8px 16px;
  border-radius: 20px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.status-dot {
  width: 8px;
  height: 8px;
  background: #10b981;
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.7; transform: scale(1.1); }
}

.status-text {
  font-size: 0.85rem;
  color: white;
  font-weight: 600;
}

/* ============================================
   MESSAGES AREA
============================================ */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  position: relative;
  z-index: 1;
}

.messages-inner {
  max-width: 1000px;
  margin: 0 auto;
  padding: 32px 24px 24px;
}

/* ============================================
   WELCOME SCREEN
============================================ */
.welcome-screen {
  text-align: center;
  padding: 60px 20px 40px;
  animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.welcome-icon-wrapper {
  width: 100px;
  height: 100px;
  margin: 0 auto 24px;
  background: white;
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 40px rgba(102, 126, 234, 0.2);
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.welcome-icon-wrapper svg {
  width: 60px;
  height: 60px;
}

.welcome-title {
  font-size: 2.5rem;
  font-weight: 800;
  color: #667eea;
  margin: 0 0 16px 0;
  letter-spacing: -1px;
}

.welcome-description {
  font-size: 1.1rem;
  color: #64748b;
  max-width: 600px;
  margin: 0 auto 48px;
  line-height: 1.7;
}

/* ============================================
   POPULAR QUESTIONS
============================================ */
.popular-questions {
  margin-top: 48px;
  animation: fadeInUp 0.6s ease-out 0.2s both;
}

.section-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  font-size: 1.3rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 24px;
}

.title-icon {
  width: 24px;
  height: 24px;
  color: #f59e0b;
}

.questions-grid {
  display: flex;
  flex-direction: column;
  gap: 14px;
  max-width: 700px;
  margin: 0 auto;
}

.question-card {
  background: white;
  border: 2px solid transparent;
  border-radius: 16px;
  padding: 20px 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  text-align: left;
}

.question-card:hover {
  border-color: #667eea;
  transform: translateY(-4px) scale(1.02);
  box-shadow: 0 12px 28px rgba(102, 126, 234, 0.25);
  background: rgba(102, 126, 234, 0.03);
}

.question-card:active {
  transform: translateY(-2px) scale(1.01);
}

.question-icon {
  width: 24px;
  height: 24px;
  color: #667eea;
  flex-shrink: 0;
}

.question-text {
  flex: 1;
  font-size: 1.05rem;
  color: #1e293b;
  font-weight: 500;
  line-height: 1.5;
}

.arrow-icon {
  width: 20px;
  height: 20px;
  color: #94a3b8;
  flex-shrink: 0;
  transition: transform 0.3s ease;
}

.question-card:hover .arrow-icon {
  transform: translateX(4px);
  color: #667eea;
}

/* ============================================
   MESSAGE WRAPPER
============================================ */
.message {
  margin-bottom: 24px;
  animation: messageSlideIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes messageSlideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-wrapper {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.user-message {
  justify-content: flex-end;
}

.assistant-message {
  justify-content: flex-start;
}

/* ============================================
   MESSAGE AVATARS
============================================ */
.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.user-avatar {
  background: #667eea;
  order: 2;
}

.user-avatar svg {
  width: 24px;
  height: 24px;
  color: white;
}

.assistant-avatar {
  background: white;
}

.assistant-avatar svg {
  width: 32px;
  height: 32px;
}

/* ============================================
   MESSAGE CONTENT
============================================ */
.message-content {
  max-width: 65%;
  padding: 18px 22px;
  border-radius: 16px;
  word-wrap: break-word;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.user-content {
  background: #667eea;
  color: white;
  border-bottom-right-radius: 4px;
}

.assistant-content {
  background: white;
  color: #1e293b;
  border-bottom-left-radius: 4px;
}

.loading-content {
  background: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 24px 32px;
}

.message-text {
  font-size: 1.05rem;
  line-height: 1.6;
  font-weight: 500;
}


/* ============================================
   HTML CONTENT STYLING
============================================ */
.html-content {
  font-size: 1.05rem;
  line-height: 1.8;
  color: #334155;
}

.html-content :deep(p) {
  margin: 0 0 14px 0;
}

.html-content :deep(p:last-child) {
  margin-bottom: 0;
}

.html-content :deep(ul),
.html-content :deep(ol) {
  margin: 14px 0;
  padding-left: 28px;
}

.html-content :deep(li) {
  margin: 8px 0;
}

.html-content :deep(strong) {
  color: #1e293b;
  font-weight: 700;
}

.html-content :deep(code) {
  background: #f1f5f9;
  color: #667eea;
  padding: 3px 8px;
  border-radius: 6px;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 0.92em;
  font-weight: 600;
}

.html-content :deep(pre) {
  background: #1e293b;
  color: #e2e8f0;
  padding: 18px;
  border-radius: 12px;
  overflow-x: auto;
  margin: 16px 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* ============================================
   SOURCES SECTION (NEW CHIP DESIGN)
============================================ */
.sources-section {
  margin-top: 18px;
  padding-top: 18px;
  border-top: 2px solid #f1f5f9;
}

.sources-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-size: 0.85rem;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.sources-icon {
  width: 16px;
  height: 16px;
  color: #667eea;
}

.sources-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.source-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  background: #f8fafc;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-size: 0.9rem;
  color: #334155;
  font-weight: 600;
  max-width: 100%;
}

.source-chip:hover {
  background: #ede9fe;
  border-color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

.source-chip:active {
  transform: translateY(0);
}

.chip-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  background: #667eea;
  color: white;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 700;
  flex-shrink: 0;
}

.chip-text {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  min-width: 0;
}

.chip-icon {
  width: 16px;
  height: 16px;
  color: #94a3b8;
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.source-chip:hover .chip-icon {
  color: #667eea;
  transform: translateX(2px) translateY(-2px);
}

/* ============================================
   MESSAGE FOOTER
============================================ */
.message-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 14px;
  padding-top: 14px;
  border-top: 2px solid #f1f5f9;
  flex-wrap: wrap;
  gap: 12px;
}

.metadata {
  display: flex;
  align-items: center;
  gap: 12px;
}

.duration {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.85rem;
  color: #64748b;
  font-weight: 600;
}

.duration svg {
  width: 16px;
  height: 16px;
}

/* ============================================
   FEEDBACK BUTTONS
============================================ */
.feedback-buttons {
  display: flex;
  gap: 10px;
}

.feedback-btn {
  width: 36px;
  height: 36px;
  background: #f8fafc;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.feedback-btn svg {
  width: 18px;
  height: 18px;
  color: #64748b;
  transition: all 0.3s ease;
}

.feedback-btn:hover {
  transform: translateY(-2px) scale(1.05);
}

.feedback-btn.thumbs-up:hover {
  background: #dbeafe;
  border-color: #3b82f6;
}

.feedback-btn.thumbs-up:hover svg {
  color: #3b82f6;
}

.feedback-btn.thumbs-down:hover {
  background: #fee2e2;
  border-color: #ef4444;
}

.feedback-btn.thumbs-down:hover svg {
  color: #ef4444;
}

.feedback-sent {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #10b981;
  font-size: 0.9rem;
  font-weight: 700;
}

.feedback-sent svg {
  width: 18px;
  height: 18px;
}

/* ============================================
   LOADING ANIMATION
============================================ */
.loading-animation {
  position: relative;
  width: 60px;
  height: 60px;
}

.dot-pulse {
  position: relative;
  left: -9999px;
  width: 12px;
  height: 12px;
  border-radius: 6px;
  background: #667eea;
  animation: dotPulse 1.5s infinite linear;
  animation-delay: 0.25s;
}

.dot-pulse::before,
.dot-pulse::after {
  content: '';
  display: inline-block;
  position: absolute;
  top: 0;
  width: 12px;
  height: 12px;
  border-radius: 6px;
  background: #667eea;
}

.dot-pulse::before {
  animation: dotPulseBefore 1.5s infinite linear;
  animation-delay: 0s;
}

.dot-pulse::after {
  animation: dotPulseAfter 1.5s infinite linear;
  animation-delay: 0.5s;
}

@keyframes dotPulseBefore {
  0% { box-shadow: 9984px 0 0 -5px; }
  30% { box-shadow: 9984px 0 0 2px; }
  60%, 100% { box-shadow: 9984px 0 0 -5px; }
}

@keyframes dotPulse {
  0% { box-shadow: 9999px 0 0 -5px; }
  30% { box-shadow: 9999px 0 0 2px; }
  60%, 100% { box-shadow: 9999px 0 0 -5px; }
}

@keyframes dotPulseAfter {
  0% { box-shadow: 10014px 0 0 -5px; }
  30% { box-shadow: 10014px 0 0 2px; }
  60%, 100% { box-shadow: 10014px 0 0 -5px; }
}

.loading-text {
  font-size: 1rem;
  color: #64748b;
  font-weight: 600;
}

.timer-display {
  font-size: 1.05rem;
  font-weight: 700;
  color: #667eea;
}

/* ============================================
   INPUT AREA
============================================ */
.chat-input-wrapper {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(226, 232, 240, 0.8);
  padding: 20px 28px 28px;
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.05);
  z-index: 10;
  position: relative;
}

.chat-input-container {
  max-width: 1000px;
  margin: 0 auto;
}

.input-group {
  display: flex;
  gap: 10px;
  align-items: center;
  background: white;
  border: 2px solid #e2e8f0;
  border-radius: 24px;
  padding: 6px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.input-group:focus-within {
  border-color: #667eea;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.25);
}


.chat-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 1.05rem;
  padding: 12px 8px;
  background: transparent;
  color: #1e293b;
  font-family: inherit;
}

.chat-input::placeholder {
  color: #94a3b8;
}

.chat-input:disabled {
  color: #cbd5e1;
  cursor: not-allowed;
}

.send-btn {
  width: 48px;
  height: 48px;
  background: #667eea;
  border: none;
  border-radius: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.send-btn svg {
  width: 22px;
  height: 22px;
  color: white;
}

.send-btn:not(:disabled):hover {
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
}

.send-btn:disabled {
  background: #e2e8f0;
  cursor: not-allowed;
  box-shadow: none;
  transform: none;
}

.send-btn:disabled svg {
  color: #94a3b8;
}

.send-btn.active {
  animation: btnPulse 2s ease-in-out infinite;
}

@keyframes btnPulse {
  0%, 100% { box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4); }
  50% { box-shadow: 0 4px 20px rgba(102, 126, 234, 0.6); }
}

.loading-icon {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  to { transform: rotate(360deg); }
}

.input-hint {
  margin-top: 10px;
  text-align: center;
  font-size: 0.85rem;
  color: #94a3b8;
  font-weight: 500;
}

/* ============================================
   SOURCE MODAL
============================================ */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-container {
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  max-width: 800px;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: modalSlideIn 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-30px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px 28px;
  border-bottom: 2px solid #f1f5f9;
  background: #f8fafc;
}

.modal-title-wrapper {
  display: flex;
  align-items: center;
  gap: 16px;
}

.modal-icon {
  width: 48px;
  height: 48px;
  padding: 12px;
  background: #667eea;
  border-radius: 12px;
  color: white;
  flex-shrink: 0;
}

.modal-title-wrapper h3 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
  letter-spacing: -0.5px;
}

.modal-subtitle {
  margin: 4px 0 0 0;
  font-size: 0.9rem;
  color: #64748b;
  font-weight: 500;
}

.modal-close {
  width: 40px;
  height: 40px;
  border: 2px solid #e2e8f0;
  background: white;
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.modal-close svg {
  width: 24px;
  height: 24px;
  color: #64748b;
  transition: all 0.3s ease;
}

.modal-close:hover {
  background: #fee2e2;
  border-color: #ef4444;
  transform: rotate(90deg);
}

.modal-close:hover svg {
  color: #ef4444;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 28px;
}

.source-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 28px;
  padding: 20px;
  background: #f8fafc;
  border-radius: 12px;
  border: 2px solid #e2e8f0;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.meta-item svg {
  width: 20px;
  height: 20px;
  color: #667eea;
  flex-shrink: 0;
}

.meta-label {
  font-size: 0.85rem;
  color: #64748b;
  font-weight: 600;
}

.meta-value {
  font-size: 0.9rem;
  color: #1e293b;
  font-weight: 700;
}

.source-question {
  margin-bottom: 28px;
  padding: 20px;
  background: #ede9fe;
  border-radius: 12px;
  border-left: 4px solid #667eea;
}

.source-question h4 {
  margin: 0 0 12px 0;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #667eea;
  font-weight: 700;
}

.source-question p {
  margin: 0;
  font-size: 1.1rem;
  color: #1e293b;
  font-weight: 600;
  line-height: 1.6;
}

.source-answer {
  padding: 20px;
  background: white;
  border-radius: 12px;
  border: 2px solid #e2e8f0;
}

.source-answer h4 {
  margin: 0 0 16px 0;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #64748b;
  font-weight: 700;
}

.answer-content {
  font-size: 1.05rem;
  line-height: 1.8;
  color: #334155;
}

.answer-content :deep(p) {
  margin: 0 0 14px 0;
}

.answer-content :deep(p:last-child) {
  margin-bottom: 0;
}

.answer-content :deep(ul),
.answer-content :deep(ol) {
  margin: 14px 0;
  padding-left: 28px;
}

.answer-content :deep(li) {
  margin: 8px 0;
}

.answer-content :deep(strong) {
  color: #1e293b;
  font-weight: 700;
}

.answer-content :deep(a) {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.2s ease;
}

.answer-content :deep(a:hover) {
  color: #764ba2;
  text-decoration: underline;
}

.answer-content :deep(code) {
  background: #f1f5f9;
  color: #667eea;
  padding: 3px 8px;
  border-radius: 6px;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 0.92em;
  font-weight: 600;
}

.modal-footer {
  padding: 20px 28px;
  border-top: 2px solid #f1f5f9;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  background: #ffffff;
}

.modal-btn {
  padding: 12px 24px;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 2px solid transparent;
}

.modal-btn-secondary {
  background: #f1f5f9;
  color: #475569;
  border-color: #e2e8f0;
}

.modal-btn-secondary:hover {
  background: #e2e8f0;
  border-color: #cbd5e1;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* Modal Fade Animation */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-active .modal-container,
.modal-fade-leave-active .modal-container {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.modal-fade-enter-from .modal-container,
.modal-fade-leave-to .modal-container {
  transform: translateY(-30px) scale(0.95);
}

/* Modal Scrollbar */
.modal-body::-webkit-scrollbar {
  width: 8px;
}

.modal-body::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 10px;
}

.modal-body::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 10px;
}

.modal-body::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* Support Form Modal */
.support-form-modal {
  background: transparent;
  box-shadow: none;
  padding: 0;
}

/* ============================================
   SCROLLBAR
============================================ */
.chat-messages::-webkit-scrollbar {
  width: 8px;
}

.chat-messages::-webkit-scrollbar-track {
  background: transparent;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: rgba(148, 163, 184, 0.5);
  border-radius: 10px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: rgba(148, 163, 184, 0.7);
}

/* ============================================
   RESPONSIVE
============================================ */
@media (max-width: 768px) {
  .chat-header {
    padding: 16px 20px;
  }

  .header-icon {
    width: 40px;
    height: 40px;
  }

  .header-icon svg {
    width: 24px;
    height: 24px;
  }

  .header-text h2 {
    font-size: 1.25rem;
  }

  .header-subtitle {
    font-size: 0.75rem;
  }

  .status-indicator {
    padding: 6px 12px;
  }

  .status-text {
    font-size: 0.75rem;
  }

  .messages-inner {
    padding: 24px 16px;
  }

  .welcome-screen {
    padding: 40px 16px 30px;
  }

  .welcome-icon-wrapper {
    width: 80px;
    height: 80px;
  }

  .welcome-icon-wrapper svg {
    width: 50px;
    height: 50px;
  }

  .welcome-title {
    font-size: 2rem;
  }

  .welcome-description {
    font-size: 1rem;
  }

  .message-content {
    max-width: 80%;
    padding: 14px 18px;
  }

  .message-avatar {
    width: 36px;
    height: 36px;
  }

  .user-avatar svg {
    width: 20px;
    height: 20px;
  }

  .assistant-avatar svg {
    width: 28px;
    height: 28px;
  }

  .chat-input-wrapper {
    padding: 16px 20px 20px;
  }

  .input-group {
    padding: 4px;
  }

  .chat-input {
    font-size: 1rem;
    padding: 10px 6px;
  }

  .send-btn {
    width: 44px;
    height: 44px;
  }

  .attach-btn {
    width: 36px;
    height: 36px;
  }
}

@media (max-width: 480px) {
  .header-content {
    gap: 12px;
  }

  .status-indicator {
    display: none;
  }

  .welcome-title {
    font-size: 1.75rem;
  }

  .question-text {
    font-size: 0.95rem;
  }

  .message-content {
    max-width: 85%;
  }
}

/* Modal Responsive */
@media (max-width: 768px) {
  .modal-overlay {
    padding: 10px;
  }

  .modal-container {
    max-height: 95vh;
    border-radius: 16px;
  }

  .modal-header {
    padding: 20px;
  }

  .modal-title-wrapper h3 {
    font-size: 1.25rem;
  }

  .modal-subtitle {
    font-size: 0.8rem;
  }

  .modal-body {
    padding: 20px;
  }

  .source-meta {
    padding: 16px;
  }

  .meta-item {
    font-size: 0.85rem;
  }

  .source-question,
  .source-answer {
    padding: 16px;
  }

  .modal-footer {
    padding: 16px 20px;
  }
}

@media (max-width: 480px) {
  .modal-icon {
    width: 40px;
    height: 40px;
    padding: 10px;
  }

  .modal-title-wrapper {
    gap: 12px;
  }

  .modal-title-wrapper h3 {
    font-size: 1.1rem;
  }

  .modal-close {
    width: 36px;
    height: 36px;
  }

  .source-meta {
    flex-direction: column;
    gap: 12px;
  }

  .meta-item {
    width: 100%;
  }
}
</style>
