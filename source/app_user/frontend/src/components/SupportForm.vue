<template>
  <div class="support-form-container">
    <div class="form-header">
      <div class="header-icon">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M20 2H4C2.9 2 2 2.9 2 4V22L6 18H20C21.1 18 22 17.1 22 16V4C22 2.9 21.1 2 20 2Z" fill="currentColor"/>
        </svg>
      </div>
      <div>
        <h3>Créer un ticket de support</h3>
        <p class="subtitle">Nous n'avons pas trouvé de réponse à votre question. Laissez-nous vos coordonnées et nous vous recontacterons.</p>
      </div>
    </div>

    <form @submit.prevent="submitForm" class="support-form">
      <div class="form-group">
        <label for="email">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M20 4H4C2.9 4 2.01 4.9 2.01 6L2 18C2 19.1 2.9 20 4 20H20C21.1 20 22 19.1 22 18V6C22 4.9 21.1 4 20 4ZM20 8L12 13L4 8V6L12 11L20 6V8Z" fill="currentColor"/>
          </svg>
          Email
        </label>
        <input
          id="email"
          v-model="formData.email"
          type="email"
          placeholder="votre.email@exemple.com"
          required
          :disabled="isSubmitting"
        />
      </div>

      <div class="form-group">
        <label for="school">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M5 13.18V17.18L12 21L19 17.18V13.18L12 17L5 13.18ZM12 3L1 9L12 15L21 10.09V17H23V9L12 3Z" fill="currentColor"/>
          </svg>
          École
        </label>
        <select
          id="school"
          v-model="formData.school"
          required
          :disabled="isSubmitting"
        >
          <option value="" disabled>Sélectionnez votre école</option>
          <option value="ESILV">ESILV</option>
          <option value="EMLV">EMLV</option>
          <option value="IIM">IIM</option>
        </select>
      </div>

      <div class="form-group">
        <label for="userType">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 12C14.21 12 16 10.21 16 8C16 5.79 14.21 4 12 4C9.79 4 8 5.79 8 8C8 10.21 9.79 12 12 12ZM12 14C9.33 14 4 15.34 4 18V20H20V18C20 15.34 14.67 14 12 14Z" fill="currentColor"/>
          </svg>
          Type d'utilisateur
        </label>
        <select
          id="userType"
          v-model="formData.userType"
          required
          :disabled="isSubmitting"
        >
          <option value="" disabled>Sélectionnez votre statut</option>
          <option value="student">Étudiant</option>
          <option value="faculty">Enseignant</option>
          <option value="staff">Personnel administratif</option>
        </select>
      </div>

      <div class="form-group">
        <label for="question">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM13 19H11V17H13V19ZM15.07 11.25L14.17 12.17C13.45 12.9 13 13.5 13 15H11V14.5C11 13.4 11.45 12.4 12.17 11.67L13.41 10.41C13.78 10.05 14 9.55 14 9C14 7.9 13.1 7 12 7C10.9 7 10 7.9 10 9H8C8 6.79 9.79 5 12 5C14.21 5 16 6.79 16 9C16 9.88 15.64 10.68 15.07 11.25Z" fill="currentColor"/>
          </svg>
          Votre question
        </label>
        <textarea
          id="question"
          v-model="formData.question"
          placeholder="Décrivez votre question en détail..."
          rows="4"
          required
          :disabled="isSubmitting"
          readonly
        ></textarea>
      </div>

      <div class="form-actions">
        <button
          type="button"
          @click="$emit('cancel')"
          class="btn btn-secondary"
          :disabled="isSubmitting"
        >
          Annuler
        </button>
        <button
          type="submit"
          class="btn btn-primary"
          :disabled="isSubmitting"
        >
          <svg v-if="!isSubmitting" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M2.01 21L23 12L2.01 3L2 10L17 12L2 14L2.01 21Z" fill="currentColor"/>
          </svg>
          <svg v-else class="loading-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 4V2C12 2 12 2 12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 9.24 20.88 6.74 19.05 5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
          {{ isSubmitting ? 'Envoi en cours...' : 'Envoyer le ticket' }}
        </button>
      </div>

      <div v-if="submitSuccess" class="success-message">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M9 16.17L4.83 12L3.41 13.41L9 19L21 7L19.59 5.59L9 16.17Z" fill="currentColor"/>
        </svg>
        Votre ticket a été créé avec succès ! Nous vous contacterons prochainement.
      </div>

      <div v-if="submitError" class="error-message">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM13 17H11V15H13V17ZM13 13H11V7H13V13Z" fill="currentColor"/>
        </svg>
        {{ submitError }}
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, defineProps, defineEmits } from 'vue';

const props = defineProps({
  initialQuestion: {
    type: String,
    required: true
  }
});

const emit = defineEmits(['cancel', 'success']);

const SUPPORT_TICKET_API_URL = 'http://localhost:3000/api/dashboard/support-ticket';

const formData = ref({
  email: '',
  school: '',
  userType: '',
  question: props.initialQuestion
});

const isSubmitting = ref(false);
const submitSuccess = ref(false);
const submitError = ref('');

const submitForm = async () => {
  isSubmitting.value = true;
  submitError.value = '';
  submitSuccess.value = false;

  try {
    const response = await fetch(SUPPORT_TICKET_API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_email: formData.value.email,
        user_school: formData.value.school,
        user_type: formData.value.userType,
        question: formData.value.question
      }),
    });

    if (!response.ok) {
      throw new Error('Erreur lors de l\'envoi du ticket');
    }

    submitSuccess.value = true;

    // Réinitialiser le formulaire après 2 secondes et émettre l'événement de succès
    setTimeout(() => {
      emit('success');
    }, 2000);

  } catch (error) {
    console.error('Erreur lors de l\'envoi du ticket:', error);
    submitError.value = 'Une erreur est survenue lors de l\'envoi de votre ticket. Veuillez réessayer.';
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
.support-form-container {
  background: white;
  border-radius: 20px;
  padding: 28px;
  box-shadow: 0 10px 40px rgba(102, 126, 234, 0.15);
  max-width: 600px;
  margin: 20px auto;
  animation: slideInUp 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.form-header {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 28px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f1f5f9;
}

.header-icon {
  width: 48px;
  height: 48px;
  background: #667eea;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.header-icon svg {
  width: 28px;
  height: 28px;
  color: white;
}

.form-header h3 {
  margin: 0 0 8px 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
}

.subtitle {
  margin: 0;
  font-size: 0.95rem;
  color: #64748b;
  line-height: 1.5;
}

.support-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  color: #334155;
}

.form-group label svg {
  width: 18px;
  height: 18px;
  color: #667eea;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 12px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 1rem;
  font-family: inherit;
  color: #1e293b;
  transition: all 0.3s ease;
  background: white;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-group input:disabled,
.form-group select:disabled,
.form-group textarea:disabled {
  background: #f8fafc;
  color: #94a3b8;
  cursor: not-allowed;
}

.form-group textarea {
  resize: vertical;
  min-height: 100px;
}

.form-group select {
  cursor: pointer;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 12px;
}

.btn {
  flex: 1;
  padding: 14px 24px;
  border: 2px solid transparent;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn svg {
  width: 20px;
  height: 20px;
}

.btn-secondary {
  background: #f1f5f9;
  color: #475569;
  border-color: #e2e8f0;
}

.btn-secondary:hover:not(:disabled) {
  background: #e2e8f0;
  border-color: #cbd5e1;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.btn-primary {
  background: #667eea;
  color: white;
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-primary:hover:not(:disabled) {
  background: #5568d3;
  border-color: #5568d3;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

.loading-icon {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  to { transform: rotate(360deg); }
}

.success-message {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #d1fae5;
  border: 2px solid #10b981;
  border-radius: 12px;
  color: #065f46;
  font-weight: 600;
  animation: slideInUp 0.4s ease;
}

.success-message svg {
  width: 24px;
  height: 24px;
  flex-shrink: 0;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #fee2e2;
  border: 2px solid #ef4444;
  border-radius: 12px;
  color: #991b1b;
  font-weight: 600;
  animation: slideInUp 0.4s ease;
}

.error-message svg {
  width: 24px;
  height: 24px;
  flex-shrink: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .support-form-container {
    padding: 20px;
    margin: 16px;
  }

  .form-header {
    flex-direction: column;
    gap: 12px;
  }

  .form-header h3 {
    font-size: 1.25rem;
  }

  .form-actions {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }
}
</style>
