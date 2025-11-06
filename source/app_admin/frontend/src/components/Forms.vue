<template>
  <div class="container">
    <h1>Tickets de Support</h1>

    <!-- Indicateur de chargement -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-spinner">
        <div class="spinner"></div>
        <p>Chargement des tickets...</p>
      </div>
    </div>

    <!-- Barre de recherche -->
    <div class="search-bar">
      <input 
        v-model="searchQuery" 
        type="text" 
        placeholder="Rechercher par email ou école..." 
        @input="handleSearch"
      />
    </div>

    <!-- Table des tickets -->
    <table>
      <thead>
        <tr>
          <th @click="sortBy('id')">ID <span v-if="sortColumn === 'id'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span></th>
          <th @click="sortBy('user_email')">Email <span v-if="sortColumn === 'user_email'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span></th>
          <th @click="sortBy('user_school')">École <span v-if="sortColumn === 'user_school'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span></th>
          <th @click="sortBy('user_type')">Type <span v-if="sortColumn === 'user_type'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span></th>
          <th>Question</th>
          <th @click="sortBy('created_at')">Date <span v-if="sortColumn === 'created_at'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="ticket in paginatedTickets" :key="ticket.id">
          <td data-label="ID">{{ ticket.id }}</td>
          <td data-label="Email" class="email-column">{{ ticket.user_email }}</td>
          <td data-label="École">
            <span :class="['school-badge', getSchoolClass(ticket.user_school)]">
              {{ ticket.user_school }}
            </span>
          </td>
          <td data-label="Type">
            <span :class="['type-badge', getTypeClass(ticket.user_type)]">
              {{ formatUserType(ticket.user_type) }}
            </span>
          </td>
          <td data-label="Question">
            <div 
              class="content-preview"
              @click="expandContent(ticket.id, ticket.question)"
            >
              <span class="text-content">{{ truncateText(ticket.question, 80) }}</span>
              <span v-if="shouldShowExpand(ticket.question)" class="expand-indicator">🔍</span>
            </div>
          </td>
          <td data-label="Date">{{ formatDate(ticket.created_at) }}</td>
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
        Page {{ currentPage }} sur {{ totalPages }} ({{ filteredTickets.length }} résultats)
      </span>
      
      <button 
        class="btn-pagination" 
        @click="currentPage++" 
        :disabled="currentPage >= totalPages"
      >
        Suivant →
      </button>
    </div>

    <!-- Modal pour afficher le contenu complet -->
    <div v-if="showContentModal" class="modal-overlay" @click="showContentModal = false">
      <div class="content-modal" @click.stop>
        <div class="content-modal-header">
          <h3>Question complète</h3>
          <div class="modal-actions">
            <button class="btn-copy" @click="copyToClipboard(expandedContent)">📋 Copier</button>
            <button class="btn-close" @click="showContentModal = false">×</button>
          </div>
        </div>
        <div class="content-modal-body">
          <div class="text-content-full">
            {{ expandedContent }}
          </div>
        </div>
        <div class="content-modal-footer">
          <span class="content-info">
            Longueur: {{ expandedContent.length }} caractères
          </span>
          <button class="btn-close-modal" @click="showContentModal = false">Fermer</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import axios from 'axios';

const tickets = ref([]);
const searchQuery = ref('');
const currentPage = ref(1);
const itemsPerPage = ref(10);
const sortColumn = ref('id');
const sortDirection = ref('desc'); // Par défaut, les plus récents en premier
const isLoading = ref(false);

// États pour le modal
const showContentModal = ref(false);
const expandedContent = ref('');

// Charger tous les tickets
const loadTickets = async () => {
  isLoading.value = true;
  try {
    const res = await axios.get('http://localhost:4000/api/forms');
    tickets.value = res.data;
  } catch (err) {
    console.error(err);
    alert('Erreur lors du chargement des tickets');
  } finally {
    isLoading.value = false;
  }
};

// Vérifier si on doit afficher l'indicateur d'expansion
const shouldShowExpand = (content) => {
  if (!content) return false;
  return content.length > 80;
};

// Tronquer le texte
const truncateText = (text, maxLength) => {
  if (!text) return '-';
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

// Afficher le contenu complet
const expandContent = (id, content) => {
  if (!content) return;
  expandedContent.value = content;
  showContentModal.value = true;
};

// Copier dans le presse-papier
const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text);
    alert('Texte copié dans le presse-papier !');
  } catch (err) {
    console.error('Erreur lors de la copie :', err);
    const textArea = document.createElement('textarea');
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.select();
    document.execCommand('copy');
    document.body.removeChild(textArea);
    alert('Texte copié dans le presse-papier !');
  }
};

// Filtrer les tickets selon la recherche
const filteredTickets = computed(() => {
  let filtered = tickets.value;
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    filtered = filtered.filter(t => 
      t.user_email.toLowerCase().includes(query) ||
      t.user_school.toLowerCase().includes(query)
    );
  }
  
  // Tri
  filtered = [...filtered].sort((a, b) => {
    let aVal = a[sortColumn.value];
    let bVal = b[sortColumn.value];
    
    if (sortColumn.value === 'created_at') {
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
  const total = filteredTickets.value.length;
  if (total === 0) return 1;
  return Math.ceil(total / itemsPerPage.value);
});

// Tickets de la page actuelle
const paginatedTickets = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value;
  const end = start + itemsPerPage.value;
  return filteredTickets.value.slice(start, end);
});

// Surveiller les changements dans filteredTickets
watch(totalPages, (newTotalPages) => {
  if (currentPage.value > newTotalPages) {
    currentPage.value = Math.max(1, newTotalPages);
  }
});

// Gérer la recherche
const handleSearch = () => {
  currentPage.value = 1;
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
  return new Date(date).toLocaleString('fr-FR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// Classe CSS pour le badge d'école
const getSchoolClass = (school) => {
  const schoolMap = {
    'EMLV': 'school-emlv',
    'ESILV': 'school-esilv',
    'IIM': 'school-iim',
    'EXECUTIVE': 'school-executive'
  };
  return schoolMap[school] || 'school-default';
};

// Classe CSS pour le badge de type
const getTypeClass = (type) => {
  const typeMap = {
    'student': 'type-student',
    'faculty': 'type-faculty',
    'staff': 'type-staff'
  };
  return typeMap[type] || 'type-default';
};

// Formater le type d'utilisateur
const formatUserType = (type) => {
  const typeNames = {
    'student': 'Étudiant',
    'faculty': 'Enseignant',
    'staff': 'Personnel'
  };
  return typeNames[type] || type;
};

onMounted(loadTickets);
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

/* Colonne Email */
.email-column {
  white-space: normal !important;
  word-wrap: break-word;
  min-width: 200px;
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

/* Badges d'école */
.school-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.school-emlv {
  background-color: #dbeafe;
  color: #1e40af;
}

.school-esilv {
  background-color: #fce7f3;
  color: #9f1239;
}

.school-iim {
  background-color: #d1fae5;
  color: #065f46;
}

.school-executive {
  background-color: #fef3c7;
  color: #92400e;
}

.school-default {
  background-color: #f3f4f6;
  color: #6b7280;
}

/* Badges de type */
.type-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.type-student {
  background-color: #e0e7ff;
  color: #3730a3;
}

.type-faculty {
  background-color: #fce7f3;
  color: #831843;
}

.type-staff {
  background-color: #e5e7eb;
  color: #374151;
}

.type-default {
  background-color: #f3f4f6;
  color: #6b7280;
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

/* Modal pour le contenu */
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

.text-content-full {
  white-space: pre-wrap;
  word-wrap: break-word;
  line-height: 1.6;
  font-size: 1rem;
  color: #374151;
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

  .pagination {
    flex-direction: column;
    gap: 1rem;
  }

  .page-info {
    order: -1;
  }
}
</style>