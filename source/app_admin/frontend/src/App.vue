<template>
  <div class="app-container">
    <!-- Header avec navigation -->
    <header class="header">
      <div class="header-content">
        <h1 class="logo">Admin page</h1>
        <nav class="nav">
          <button 
            :class="['nav-btn', { active: currentPage === 'dashboard' }]"
            @click="currentPage = 'dashboard'"
          >
            🏠 Dashboard
          </button>
          <button 
            :class="['nav-btn', { active: currentPage === 'questions' }]"
            @click="currentPage = 'questions'"
          >
            📝 Gérer les Questions
          </button>
          <button 
            :class="['nav-btn', { active: currentPage === 'forms' }]"
            @click="currentPage = 'forms'"
          >
            📋 Tickets de Support
          </button>
        </nav>
      </div>
    </header>

    <!-- Contenu principal -->
    <main class="main-content">
      <!-- Page Dashboard -->
      <Dashboard v-if="currentPage === 'dashboard'" />
      <!-- Page Gestion des Questions -->
      <Questions v-if="currentPage === 'questions'" />
      <!-- Page Tickets de Support -->
      <Forms v-if="currentPage === 'forms'" />
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import Questions from '@/components/Questions.vue';
import Dashboard from '@/components/Dashboard.vue';
import Forms from '@/components/Forms.vue';

const currentPage = ref('dashboard');
</script>

<style scoped>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}


.app-container {
  min-height: 100vh;
  background-color: #f8fafc;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Header */
.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1800px;
  margin: 0 auto;
  padding: 1.5rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 1.75rem;
  font-weight: 700;
  color: white;
  margin: 0;
}

/* Navigation */
.nav {
  display: flex;
  gap: 1rem;
}

.nav-btn {
  padding: 0.75rem 1.5rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.nav-btn:hover {
  background-color: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-2px);
}

.nav-btn.active {
  background-color: white;
  color: #667eea;
  border-color: white;
}

/* Contenu principal */
.main-content {
  max-width: 1800px;
  margin: 0 auto;
}

.dashboard-page {
  padding: 2rem;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 2rem;
  text-align: center;
}

/* Placeholder Dashboard */
.dashboard-placeholder {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
}

.placeholder-card {
  background: white;
  padding: 4rem;
  border-radius: 24px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  text-align: center;
  max-width: 500px;
}

.placeholder-icon {
  font-size: 5rem;
  margin-bottom: 1.5rem;
}

.placeholder-card h3 {
  font-size: 1.75rem;
  color: #1e293b;
  margin-bottom: 1rem;
}

.placeholder-card p {
  font-size: 1.1rem;
  color: #64748b;
  line-height: 1.6;
}

/* Responsive */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
  }

  .logo {
    font-size: 1.5rem;
  }

  .nav {
    width: 100%;
    flex-direction: column;
  }

  .nav-btn {
    width: 100%;
  }

  .dashboard-page {
    padding: 1rem;
  }

  .page-title {
    font-size: 1.75rem;
  }

  .placeholder-card {
    padding: 2rem;
  }

  .placeholder-icon {
    font-size: 3rem;
  }

  .placeholder-card h3 {
    font-size: 1.5rem;
  }

  .placeholder-card p {
    font-size: 1rem;
  }
}
</style>