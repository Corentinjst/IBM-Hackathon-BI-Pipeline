<template>
  <div class="container">
    <h1>Liste des questions</h1>

    <!-- Indicateur de chargement -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-spinner">
        <div class="spinner"></div>
        <p>Chargement des questions...</p>
      </div>
    </div>

    <!-- Barre de recherche -->
    <div class="search-bar">
      <input 
        v-model="searchQuery" 
        type="text" 
        placeholder="Rechercher par titre " 
        @input="handleSearch"
      />
    </div>

    <!-- Table des questions -->
    <table>
      <thead>
        <tr>
          <th @click="sortBy('id')">ID <span v-if="sortColumn === 'id'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span></th>
          <th @click="sortBy('title')">Titre <span v-if="sortColumn === 'title'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span></th>
          <th>Contenu</th>
          <th @click="sortBy('post_type')">Type <span v-if="sortColumn === 'post_type'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span></th>
          <th @click="sortBy('langues')">Langues <span v-if="sortColumn === 'langues'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span></th>
          <th>Thématiques</th>
          <th>Utilisateurs</th>
          <th>Écoles</th>
          <th @click="sortBy('status')">Statut <span v-if="sortColumn === 'status'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span></th>
          <th @click="sortBy('date')">Date <span v-if="sortColumn === 'date'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span></th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="question in paginatedQuestions" :key="question.id">
          <td data-label="ID">{{ question.id }}</td>
          <td data-label="Titre" class="title-column">
            {{ question.title }}
          </td>
          <td data-label="Contenu">
            <div 
              class="content-preview"
              :class="{ 'has-html': containsHTML(question.content) }"
              @click="expandContent(question.id, question.content)"
            >
              <div v-if="containsHTML(question.content)" class="html-content" v-html="truncateHTML(question.content, 100)"></div>
              <span v-else class="text-content">{{ truncateText(question.content, 50) }}</span>
              
              <span v-if="shouldShowExpand(question.content)" class="expand-indicator">🔍</span>
            </div>
          </td>
          <td data-label="Type">{{ question.post_type || '-' }}</td>
          <td data-label="Langues">{{ question.langues || '-' }}</td>
          <td data-label="Thématiques">
            <span 
              class="expandable-text" 
              :class="{ 'truncated': shouldTruncate(question.thematiques, 30) }"
              @click="expandText(question.id, 'thematiques', question.thematiques)"
            >
              {{ question.thematiques || '-' }}
            </span>
          </td>
          <td data-label="Utilisateurs">
            <span 
              class="expandable-text" 
              :class="{ 'truncated': shouldTruncate(question.utilisateurs, 30) }"
              @click="expandText(question.id, 'utilisateurs', question.utilisateurs)"
            >
              {{ question.utilisateurs || '-' }}
            </span>
          </td>
          <td data-label="Écoles">
            <span 
              class="expandable-text" 
              :class="{ 'truncated': shouldTruncate(question.ecoles, 30) }"
              @click="expandText(question.id, 'ecoles', question.ecoles)"
            >
              {{ question.ecoles || '-' }}
            </span>
          </td>
          <td data-label="Statut">
            <span :class="['status-badge', getStatusClass(question.status)]">
              {{ question.status || '-' }}
            </span>
          </td>
          <td data-label="Date">{{ formatDate(question.date) }}</td>
          <td data-label="Actions" class="actions-cell">
            <button class="btn-edit" @click="editQuestion(question)">✏️</button>
            <button class="btn-delete" @click="deleteQuestion(question.id)">🗑️</button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Pagination -->
    <div class="pagination">
      <button 
        class="btn-pagination" 
        @click="currentPage--" 
        :disabled="currentPage === 1"
      >
        ← Précédent
      </button>
      
      <span class="page-info">
        Page {{ currentPage }} sur {{ totalPages }} ({{ filteredQuestions.length }} résultats)
      </span>
      
      <button 
        class="btn-pagination" 
        @click="currentPage++" 
        :disabled="currentPage >= totalPages"
      >
        Suivant →
      </button>
    </div>

    <!-- Bouton pour ajouter une question -->
    <button class="btn-add" @click="showForm = true; resetForm()">+ Ajouter une question</button>

    <!-- Modal pour afficher le contenu complet -->
    <div v-if="showContentModal" class="modal-overlay" @click="showContentModal = false">
      <div class="content-modal" @click.stop>
        <div class="content-modal-header">
          <h3>Contenu complet</h3>
          <div class="modal-actions">
            <button class="btn-copy" @click="copyToClipboard(expandedContent)">📋 Copier</button>
            <button class="btn-toggle" @click="toggleViewMode">
              {{ viewMode === 'html' ? '📝 Texte' : '🌐 HTML' }}
            </button>
            <button class="btn-close" @click="showContentModal = false">×</button>
          </div>
        </div>
        <div class="content-modal-body">
          <div 
            v-if="viewMode === 'html'" 
            class="html-content-full"
            v-html="expandedContent"
          ></div>
          <div 
            v-else 
            class="text-content-full"
          >
            {{ expandedContent }}
          </div>
        </div>
        <div class="content-modal-footer">
          <span class="content-info">
            Affichage: {{ viewMode === 'html' ? 'HTML' : 'Texte brut' }} 
            | Longueur: {{ expandedContent.length }} caractères
          </span>
          <button class="btn-close-modal" @click="showContentModal = false">Fermer</button>
        </div>
      </div>
    </div>

    <!-- Modal pour afficher le texte simple -->
    <div v-if="showTextModal" class="modal-overlay" @click="showTextModal = false">
      <div class="text-modal" @click.stop>
        <div class="text-modal-header">
          <h3>Contenu complet - {{ expandedField }}</h3>
          <button class="btn-close" @click="showTextModal = false">×</button>
        </div>
        <div class="text-modal-content">
          <p>{{ expandedText }}</p>
        </div>
        <div class="text-modal-actions">
          <button class="btn-copy" @click="copyToClipboard(expandedText)">📋 Copier</button>
          <button class="btn-close-modal" @click="showTextModal = false">Fermer</button>
        </div>
      </div>
    </div>

    <!-- Formulaire modal -->
    <div v-if="showForm" class="modal-overlay">
      <div class="modal">
        <h2>{{ editingQuestion ? 'Modifier la question' : 'Ajouter une question' }}</h2>

        <form @submit.prevent="submitForm">
          <div class="form-group">
            <label>Titre *</label>
            <input v-model="form.title" type="text" required />
          </div>

          <div class="form-group">
            <label>Contenu *</label>
            <textarea v-model="form.content" required rows="5"></textarea>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Type de post</label>
              <textarea v-model="form.post_type" required rows="1"></textarea>
            </div>

            <div class="form-group">
              <label>Statut</label>
              <textarea v-model="form.status" required rows="1"></textarea>

            </div>
          </div>

          <div class="form-group">
            <label>Langues</label>
            <input v-model="form.langues" type="text" placeholder="Ex: Français, Anglais" />
          </div>

          <div class="form-group">
            <label>Thématiques</label>
            <textarea v-model="form.thematiques" rows="2" placeholder="Ex: Sciences, Mathématiques, Histoire"></textarea>
          </div>

          <div class="form-group">
            <label>Utilisateurs</label>
            <textarea v-model="form.utilisateurs" rows="2" placeholder="Noms des utilisateurs concernés"></textarea>
          </div>

          <div class="form-group">
            <label>Écoles</label>
            <textarea v-model="form.ecoles" rows="2" placeholder="Noms des écoles concernées"></textarea>
          </div>

          <div class="form-group">
            <label>Date *</label>
            <input v-model="form.date" type="date" required />
          </div>

          <div class="form-actions">
            <button type="button" class="btn-cancel" @click="showForm = false">Annuler</button>
            <button type="submit" class="btn-submit">{{ editingQuestion ? 'Mettre à jour' : 'Ajouter' }}</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import axios from 'axios';

const questions = ref([]);
const showForm = ref(false);
const editingQuestion = ref(null);
const searchQuery = ref('');
const currentPage = ref(1);
const itemsPerPage = ref(10);
const sortColumn = ref('id');
const sortDirection = ref('asc');
const isLoading = ref(false); // État de chargement

// États pour les modals
const showTextModal = ref(false);
const showContentModal = ref(false);
const expandedText = ref('');
const expandedContent = ref('');
const expandedField = ref('');
const viewMode = ref('html'); // 'html' ou 'text'

const form = ref({
  title: '',
  content: '',
  date: '',
  post_type: '',
  langues: '',
  thematiques: '',
  utilisateurs: '',
  ecoles: '',
  status: ''
});

// Charger TOUTES les questions
const loadQuestions = async () => {
  isLoading.value = true; // Activer le loading
  try {
    const res = await axios.get('http://localhost:4000/api/questions');
    questions.value = res.data;
  } catch (err) {
    console.error(err);
    alert('Erreur lors du chargement des questions');
  } finally {
    isLoading.value = false; // Désactiver le loading
  }
};

// Vérifier si le texte doit être tronqué
const shouldTruncate = (text, maxLength) => {
  if (!text || text === '-') return false;
  return text.length > maxLength;
};

// Vérifier si le contenu contient du HTML
const containsHTML = (text) => {
  if (!text) return false;
  return /<[a-z][\s\S]*>/i.test(text);
};

// Vérifier si on doit afficher l'indicateur d'expansion
const shouldShowExpand = (content) => {
  if (!content || content === '-') return false;
  return content.length > 50 || containsHTML(content);
};

// Tronquer le HTML sans casser les balises
const truncateHTML = (html, maxLength) => {
  if (!html) return '';
  if (html.length <= maxLength) return html;
  
  // Supprimer les balises pour compter les caractères textuels
  const textContent = html.replace(/<[^>]*>/g, '');
  if (textContent.length <= maxLength) return html;
  
  // Tronquer le texte et garder les balises intactes
  let truncated = '';
  let charCount = 0;
  let inTag = false;
  let tagContent = '';
  
  for (let i = 0; i < html.length; i++) {
    const char = html[i];
    
    if (char === '<') {
      inTag = true;
      tagContent = char;
    } else if (char === '>' && inTag) {
      tagContent += char;
      truncated += tagContent;
      inTag = false;
      tagContent = '';
    } else if (inTag) {
      tagContent += char;
    } else {
      if (charCount < maxLength) {
        truncated += char;
        charCount++;
      } else {
        break;
      }
    }
  }
  
  return truncated + '...';
};

// Afficher le contenu (gère HTML et texte)
const expandContent = (id, content) => {
  if (!content || content === '-') return;
  expandedContent.value = content;
  viewMode.value = containsHTML(content) ? 'html' : 'text';
  showContentModal.value = true;
};

// Afficher le texte simple (pour les autres colonnes)
const expandText = (id, field, text) => {
  if (!text || text === '-') return;
  expandedText.value = text;
  expandedField.value = field;
  showTextModal.value = true;
};

// Basculer entre les modes d'affichage
const toggleViewMode = () => {
  viewMode.value = viewMode.value === 'html' ? 'text' : 'html';
};

// Copier dans le presse-papier
const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text);
    alert('Texte copié dans le presse-papier !');
  } catch (err) {
    console.error('Erreur lors de la copie :', err);
    // Fallback pour les anciens navigateurs
    const textArea = document.createElement('textarea');
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.select();
    document.execCommand('copy');
    document.body.removeChild(textArea);
    alert('Texte copié dans le presse-papier !');
  }
};

// Tronquer le texte simple
const truncateText = (text, maxLength) => {
  if (!text || text === '-') return '-';
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

// Filtrer les questions selon la recherche
const filteredQuestions = computed(() => {
  let filtered = questions.value;
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    filtered = filtered.filter(q => 
      q.title.toLowerCase().includes(query)
    );
  }
  
  // Tri
  filtered = [...filtered].sort((a, b) => {
    let aVal = a[sortColumn.value];
    let bVal = b[sortColumn.value];
    
    if (sortColumn.value === 'date') {
      aVal = new Date(aVal);
      bVal = new Date(bVal);
    }
    
    if (sortDirection.value === 'asc') {
      return aVal > bVal ? 1 : -1;
    } else {
      return aVal < bVal ? 1 : -1;
    }
  });
  
  return filtered;
});

// Calculer le nombre total de pages
const totalPages = computed(() => {
  const total = filteredQuestions.value.length;
  if (total === 0) return 1;
  return Math.ceil(total / itemsPerPage.value);
});

// Questions de la page actuelle
const paginatedQuestions = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value;
  const end = start + itemsPerPage.value;
  return filteredQuestions.value.slice(start, end);
});

// Surveiller les changements dans filteredQuestions pour ajuster currentPage si nécessaire
watch(totalPages, (newTotalPages) => {
  if (currentPage.value > newTotalPages) {
    currentPage.value = Math.max(1, newTotalPages);
  }
});

// Gérer la recherche
const handleSearch = () => {
  currentPage.value = 1; // Retour à la première page lors de la recherche
};

// Gérer le tri
const sortBy = (column) => {
  if (sortColumn.value === column) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortColumn.value = column;
    sortDirection.value = 'asc';
  }
};

// Formater la date
const formatDate = (date) => {
  return new Date(date).toLocaleDateString('fr-FR');
};

// Classe CSS pour le badge de statut
const getStatusClass = (status) => {
  const statusMap = {
    'En attente': 'status-pending',
    'Approuvé': 'status-approved',
    'Rejeté': 'status-rejected',
    'Archivé': 'status-archived'
  };
  return statusMap[status] || 'status-default';
};

const resetForm = () => {
  form.value = { 
    title: '', 
    content: '', 
    date: '',
    post_type: '',
    langues: '',
    thematiques: '',
    utilisateurs: '',
    ecoles: '',
    status: ''
  };
  editingQuestion.value = null;
};

const submitForm = async () => {
  isLoading.value = true; // Activer le loading
  try {
    if (editingQuestion.value) {
      await axios.put(`http://localhost:4000/api/questions/${editingQuestion.value.id}`, form.value);
      alert('Question mise à jour');
    } else {
      await axios.post('http://localhost:4000/api/questions', form.value);
      alert('Question ajoutée');
    }
    showForm.value = false;
    loadQuestions();
  } catch (err) {
    console.error(err);
    alert('Erreur lors de la sauvegarde');
    isLoading.value = false; // Désactiver le loading en cas d'erreur
  }
};

const editQuestion = (q) => {
  form.value = { 
    title: q.title, 
    content: q.content, 
    date: q.date,
    post_type: q.post_type || '',
    langues: q.langues || '',
    thematiques: q.thematiques || '',
    utilisateurs: q.utilisateurs || '',
    ecoles: q.ecoles || '',
    status: q.status || ''
  };
  editingQuestion.value = q;
  showForm.value = true;
};

const deleteQuestion = async (id) => {
  if (!confirm('Voulez-vous vraiment supprimer cette question ?')) return;
  isLoading.value = true; // Activer le loading
  try {
    await axios.delete(`http://localhost:4000/api/questions/${id}`);
    alert('Question supprimée');
    loadQuestions();
  } catch (err) {
    console.error(err);
    alert('Erreur lors de la suppression');
    isLoading.value = false; // Désactiver le loading en cas d'erreur
  }
};

onMounted(loadQuestions);
</script>

<style scoped>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

.container {
  max-width: 1800px;
  margin: 0 auto;
  padding: 2rem;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f8fafc;
  min-height: 100vh;
}

h1 {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 2rem;
  text-align: center;
}

/* Indicateur de chargement */
.loading-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
  backdrop-filter: blur(4px);
}

.loading-spinner {
  background-color: white;
  padding: 2rem 3rem;
  border-radius: 16px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  text-align: center;
  animation: slideIn 0.3s ease;
}

.loading-spinner p {
  margin-top: 1rem;
  font-size: 1.1rem;
  color: #475569;
  font-weight: 500;
}

/* Spinner animé */
.spinner {
  width: 50px;
  height: 50px;
  margin: 0 auto;
  border: 4px solid #e2e8f0;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Barre de recherche */
.search-bar {
  margin-bottom: 1.5rem;
}

.search-bar input {
  width: 100%;
  padding: 0.875rem 1rem;
  font-size: 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  outline: none;
  transition: all 0.3s ease;
  background-color: white;
}

.search-bar input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Tableau */
table {
  width: 100%;
  background-color: white;
  border-radius: 16px;
  overflow-x: auto;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin: 0 auto;
  display: block;
}

thead {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: table;
  width: 100%;
  table-layout: fixed;
}

thead th {
  color: white;
  padding: 1rem;
  text-align: center;
  font-weight: 600;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  cursor: pointer;
  user-select: none;
  transition: background-color 0.2s;
  white-space: nowrap;
}

thead th:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

thead th span {
  margin-left: 0.5rem;
  font-size: 1rem;
}

tbody {
  display: table;
  width: 100%;
  table-layout: fixed;
}

tbody td {
  padding: 1rem;
  border-bottom: 1px solid #f1f5f9;
  color: #475569;
  font-size: 0.9rem;
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
}

tbody tr {
  transition: background-color 0.2s;
  display: table-row;
}

tbody tr:hover {
  background-color: #f8fafc;
}

tbody tr:last-child td {
  border-bottom: none;
}

/* Colonne Titre - toujours affichée en entier */
.title-column {
  white-space: normal !important;
  word-wrap: break-word;
  min-width: 150px;
}

/* Prévisualisation du contenu */
.content-preview {
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  max-height: 60px;
  overflow: hidden;
}

.content-preview:hover {
  background-color: #f1f5f9;
  border-radius: 6px;
  padding: 4px 8px;
  margin: -4px -8px;
}

.content-preview.has-html {
  text-align: left;
}

.html-content {
  font-size: 0.85rem;
  line-height: 1.4;
}

.html-content :deep(*) {
  margin: 0;
  padding: 0;
  line-height: inherit;
}

.html-content :deep(p) {
  margin-bottom: 0.25em;
}

.html-content :deep(strong) {
  font-weight: 600;
}

.html-content :deep(em) {
  font-style: italic;
}

.html-content :deep(ul) {
  padding-left: 1em;
  list-style-type: disc;
}

.html-content :deep(ol) {
  padding-left: 1em;
  list-style-type: decimal;
}

.html-content :deep(li) {
  margin-bottom: 0.25em;
}

.text-content {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.expand-indicator {
  position: absolute;
  top: 2px;
  right: 2px;
  background: rgba(255, 255, 255, 0.9);
  padding: 2px 4px;
  border-radius: 4px;
  font-size: 0.7em;
  opacity: 0.7;
}

.content-preview:hover .expand-indicator {
  opacity: 1;
}

/* Texte expansible pour autres colonnes */
.expandable-text {
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-block;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.expandable-text.truncated {
  color: #3b82f6;
  font-weight: 500;
  position: relative;
}

.expandable-text.truncated:hover {
  background-color: #f1f5f9;
  border-radius: 4px;
  padding: 2px 4px;
}

.expandable-text.truncated::after {
  content: " 🔍";
  font-size: 0.8em;
  opacity: 0.7;
}

.actions-cell {
  justify-content: center;
}

/* Badge de statut */
.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-pending {
  background-color: #fef3c7;
  color: #92400e;
}

.status-approved {
  background-color: #d1fae5;
  color: #065f46;
}

.status-rejected {
  background-color: #fee2e2;
  color: #991b1b;
}

.status-archived {
  background-color: #e5e7eb;
  color: #374151;
}

.status-default {
  background-color: #f3f4f6;
  color: #6b7280;
}

/* Boutons d'action dans le tableau */
.btn-edit,
.btn-delete {
  padding: 0.5rem 0.875rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1.1rem;
  transition: all 0.2s;
}

.btn-edit {
  background-color: #3b82f6;
}

.btn-edit:hover {
  background-color: #2563eb;
  transform: translateY(-2px);
}

.btn-delete {
  background-color: #ef4444;
}

.btn-delete:hover {
  background-color: #dc2626;
  transform: translateY(-2px);
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 2rem 0;
  padding: 1rem;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.page-info {
  font-weight: 500;
  color: #475569;
  font-size: 1rem;
}

.btn-pagination {
  padding: 0.625rem 1.25rem;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-pagination:hover:not(:disabled) {
  background-color: #2563eb;
  transform: translateY(-2px);
}

.btn-pagination:disabled {
  background-color: #cbd5e1;
  cursor: not-allowed;
  transform: none;
}

/* Bouton Ajouter */
.btn-add {
  width: 100%;
  padding: 1rem;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 6px rgba(16, 185, 129, 0.2);
}

.btn-add:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(16, 185, 129, 0.3);
}

/* Modal pour le contenu HTML/Text */
.content-modal {
  background-color: white;
  border-radius: 16px;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  animation: slideUp 0.3s ease;
  display: flex;
  flex-direction: column;
}

.content-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
  flex-shrink: 0;
}

.content-modal-header h3 {
  margin: 0;
  color: #1e293b;
  font-size: 1.25rem;
}

.modal-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.btn-toggle {
  background: none;
  border: 1px solid #d1d5db;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.btn-toggle:hover {
  background-color: #f3f4f6;
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #64748b;
  padding: 0.25rem;
  border-radius: 4px;
  transition: all 0.2s;
  margin-left: 0.5rem;
}

.btn-close:hover {
  background-color: #f1f5f9;
  color: #374151;
}

.content-modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  background-color: #f8fafc;
  margin: 0;
}

.html-content-full {
  line-height: 1.6;
  font-size: 1rem;
}

.html-content-full :deep(*) {
  margin-bottom: 1em;
  line-height: inherit;
}

.html-content-full :deep(p) {
  margin-bottom: 1em;
}

.html-content-full :deep(ul), 
.html-content-full :deep(ol) {
  margin-bottom: 1em;
  padding-left: 2em;
}

.html-content-full :deep(li) {
  margin-bottom: 0.5em;
}

.html-content-full :deep(blockquote) {
  border-left: 4px solid #e2e8f0;
  padding-left: 1em;
  margin-left: 0;
  color: #64748b;
  font-style: italic;
}

.text-content-full {
  white-space: pre-wrap;
  word-wrap: break-word;
  line-height: 1.6;
  font-size: 1rem;
}

.content-modal-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-top: 1px solid #e2e8f0;
  flex-shrink: 0;
}

.content-info {
  font-size: 0.875rem;
  color: #64748b;
}

.btn-copy,
.btn-close-modal {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.9rem;
}

.btn-copy {
  background-color: #3b82f6;
  color: white;
}

.btn-copy:hover {
  background-color: #2563eb;
  transform: translateY(-1px);
}

.btn-close-modal {
  background-color: #6b7280;
  color: white;
}

.btn-close-modal:hover {
  background-color: #4b5563;
  transform: translateY(-1px);
}

/* Modal pour le texte simple */
.text-modal {
  background-color: white;
  border-radius: 16px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  animation: slideUp 0.3s ease;
  display: flex;
  flex-direction: column;
}

.text-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 1.5rem 1rem;
  border-bottom: 1px solid #e2e8f0;
}

.text-modal-header h3 {
  margin: 0;
  color: #1e293b;
  font-size: 1.25rem;
}

.text-modal-content {
  padding: 1.5rem;
  flex: 1;
  overflow-y: auto;
  background-color: #f8fafc;
  margin: 0 1.5rem;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.text-modal-content p {
  margin: 0;
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
  color: #374151;
}

.text-modal-actions {
  display: flex;
  gap: 1rem;
  padding: 1rem 1.5rem 1.5rem;
  border-top: 1px solid #e2e8f0;
}

/* Modal principal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
  overflow-y: auto;
  padding: 2rem 0;
}

.modal {
  background-color: white;
  padding: 2rem;
  border-radius: 20px;
  width: 90%;
  max-width: 700px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  animation: slideUp 0.3s ease;
  margin: auto;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal h2 {
  font-size: 1.75rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  color: #1e293b;
}

/* Formulaire */
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #334155;
  font-size: 0.95rem;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  font-size: 1rem;
  font-family: inherit;
  transition: all 0.2s;
  outline: none;
}

.form-group select {
  cursor: pointer;
  background-color: white;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-group textarea {
  resize: vertical;
  min-height: 60px;
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
}

.btn-cancel,
.btn-submit {
  flex: 1;
  padding: 0.875rem;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 1rem;
}

.btn-cancel {
  background-color: #e2e8f0;
  color: #475569;
}

.btn-cancel:hover {
  background-color: #cbd5e1;
}

.btn-submit {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  box-shadow: 0 4px 6px rgba(59, 130, 246, 0.2);
}

.btn-submit:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(59, 130, 246, 0.3);
}

/* Responsive */
@media (max-width: 768px) {
  .container {
    padding: 1rem;
  }

  h1 {
    font-size: 1.75rem;
  }

  table, thead, tbody, th, td, tr {
    display: block;
  }

  thead tr {
    display: none;
  }

  tbody tr {
    margin-bottom: 1rem;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  tbody td {
    display: flex;
    justify-content: space-between;
    padding: 0.75rem 1rem;
    text-align: right;
  }

  tbody td::before {
    content: attr(data-label);
    font-weight: 600;
    text-align: left;
    color: #64748b;
  }

  .actions-cell {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 1rem;
  }

  .actions-cell::before {
    content: "Actions";
    font-weight: 600;
    color: #64748b;
    margin-right: auto;
  }
  .pagination {
    flex-direction: column;
    gap: 1rem;
  }

  .page-info {
    order: -1;
  }

  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>