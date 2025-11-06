<template>
  <div class="dashboard">
    <h1>📊 Dashboard - Analyse des réponses</h1>

    <!-- Première ligne : Camembert + Requêtes par jour -->
    <div class="main-row">
      <!-- 1. Camembert -->
      <div class="card small-pie-card">
        <h2>1️⃣ Pourcentage de réponses utiles</h2>
        <canvas id="pieChart"></canvas>
      </div>

      <!-- 2. Utilité vs Score de similarité -->
      <div class="card">
        <h2>2️⃣ Utilité vs Score de similarité</h2>
        <canvas id="scatterPlot"></canvas>
      </div>

    </div>

    <!-- Deuxième ligne : Questions plus/moins posées -->
    <div class="main-row">
      <!-- 3. Questions les plus posées -->
      <div class="card">
        <h2>3️⃣ Questions les plus posées</h2>
        <canvas id="mostAskedChart"></canvas>
      </div>

      <!-- 4. Questions les moins posées -->
      <div class="card">
        <h2>4️⃣ Questions les moins posées</h2>
        <canvas id="leastAskedChart"></canvas>
      </div>
    </div>

    <!-- Troisième ligne : Temps de réponse + Scatter plot -->
    <div class="main-row">
      <!-- 5. Temps de réponse moyen par jour -->
      <div class="card">
        <h2>5️⃣ Temps de réponse moyen par jour</h2>
        <canvas id="responseTimeChart"></canvas>
      </div>

      <!-- 2. Nombre de requêtes par jour -->
      <div class="card">
        <h2>6️⃣ Nombre de requêtes par jour</h2>
        <canvas id="requestsPerDayChart"></canvas>
      </div>
      
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import axios from "axios";
import { Chart, registerables } from "chart.js";
Chart.register(...registerables);

const feedbackData = ref([]);

// Charger les données du feedback
const loadData = async () => {
  try {
    const res = await axios.get('http://localhost:4000/api/dashboard');
    feedbackData.value = res.data;
    createCharts();
  } catch (err) {
    console.error('Erreur lors du chargement des données:', err);
    alert('Erreur lors du chargement des données');
  }
};

const createCharts = () => {
  if (!feedbackData.value.length) return;

  // --- 1. Camembert - Statistiques d'utilité ---
  const utileCount = feedbackData.value.filter(d => d.was_helpful === 1).length;
  const nonUtileCount = feedbackData.value.filter(d => d.was_helpful === 0).length;
  const sansReponseCount = feedbackData.value.filter(d => d.was_helpful === null).length;

  new Chart(document.getElementById("pieChart"), {
    type: "pie",
    data: {
      labels: ["Utile", "Non utile", "Sans réponse"],
      datasets: [{ 
        data: [utileCount, nonUtileCount, sansReponseCount], 
        backgroundColor: ["#4CAF50", "#F44336", "#9E9E9E"] 
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: 'bottom',
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              const total = context.dataset.data.reduce((a,b)=>a+b,0);
              const value = context.raw;
              const pct = total > 0 ? ((value/total)*100).toFixed(1) : 0;
              return `${context.label}: ${value} (${pct}%)`;
            }
          }
        }
      }
    }
  });

  // --- 2. Nombre de requêtes par jour ---
  const requestsByDay = {};
  
  feedbackData.value.forEach(d => {
    if (d.timestamp) {
      const date = new Date(d.timestamp).toISOString().split('T')[0]; // YYYY-MM-DD
      requestsByDay[date] = (requestsByDay[date] || 0) + 1;
    }
  });

  const sortedDates = Object.keys(requestsByDay).sort();
  const requestCounts = sortedDates.map(date => requestsByDay[date]);

  new Chart(document.getElementById("requestsPerDayChart"), {
    type: "bar",
    data: {
      labels: sortedDates,
      datasets: [{
        label: "Nombre de requêtes",
        data: requestCounts,
        backgroundColor: "rgba(255, 159, 64, 0.6)",
        borderColor: "rgba(255, 159, 64, 1)",
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: "Nombre de requêtes"
          },
          ticks: {
            stepSize: 1
          }
        },
        x: {
          title: {
            display: true,
            text: "Date"
          }
        }
      }
    }
  });

  // --- 3. Questions les plus posées ---
  const questionCount = {};
  
  feedbackData.value.forEach(d => {
    const questionKey = d.matched_question_title || 'Question non identifiée';
    questionCount[questionKey] = (questionCount[questionKey] || 0) + 1;
  });

  const sortedQuestions = Object.entries(questionCount)
    .sort((a,b) => b[1]-a[1])
    .map(([q,count])=>({q,count}));

  // Questions les plus posées (top 5)
  const topQuestions = sortedQuestions.slice(0,5);
  new Chart(document.getElementById("mostAskedChart"), {
    type: "bar",
    data: { 
      labels: topQuestions.map(q=>q.q), 
      datasets:[{ 
        label:"Nombre de fois posée", 
        data:topQuestions.map(q=>q.count), 
        backgroundColor:"#2196F3"
      }]
    },
    options:{ 
      indexAxis:"y", 
      responsive: true,
      scales:{ 
        x:{ 
          beginAtZero:true,
          ticks: { stepSize: 1 }
        }
      }
    }
  });

  // --- 4. Questions les moins posées (bottom 5) ---
  const leastQuestions = sortedQuestions.slice(-5).reverse();
  new Chart(document.getElementById("leastAskedChart"), {
    type: "bar",
    data: { 
      labels: leastQuestions.map(q=>q.q), 
      datasets:[{ 
        label:"Nombre de fois posée", 
        data:leastQuestions.map(q=>q.count), 
        backgroundColor:"#FF9800"
      }]
    },
    options:{ 
      indexAxis:"y", 
      responsive: true,
      scales:{ 
        x:{ 
          beginAtZero:true,
          ticks: { stepSize: 1 }
        }
      }
    }
  });

  // --- 5. Temps de réponse moyen par jour ---
  const responseTimesByDay = {};
  
  feedbackData.value.forEach(d => {
    if (d.timestamp && d.response_time_ms) {
      const date = new Date(d.timestamp).toISOString().split('T')[0];
      if (!responseTimesByDay[date]) {
        responseTimesByDay[date] = [];
      }
      responseTimesByDay[date].push(d.response_time_ms);
    }
  });

  const sortedResponseDates = Object.keys(responseTimesByDay).sort();
  const averageResponseTimes = sortedResponseDates.map(date => {
    const times = responseTimesByDay[date];
    return times.reduce((a, b) => a + b, 0) / times.length;
  });

  new Chart(document.getElementById("responseTimeChart"), {
    type: "line",
    data: {
      labels: sortedResponseDates,
      datasets: [{
        label: "Temps de réponse moyen (ms)",
        data: averageResponseTimes,
        backgroundColor: "rgba(153, 102, 255, 0.2)",
        borderColor: "rgba(153, 102, 255, 1)",
        borderWidth: 2,
        tension: 0.3,
        fill: true
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: "Temps (ms)"
          }
        },
        x: {
          title: {
            display: true,
            text: "Date"
          }
        }
      }
    }
  });

  // --- 6. Scatter plot Utilité vs Score de similarité ---
  const scatterData = feedbackData.value
    .filter(d => d.similarity_score !== null && d.was_helpful !== null)
    .map(d => ({
      x: d.similarity_score,
      y: d.was_helpful,
      helpfulText: d.was_helpful === 1 ? 'Utile' : 'Non utile'
    }));

  new Chart(document.getElementById("scatterPlot"), {
    type: "scatter",
    data: {
      datasets: [
        {
          label: "Utile",
          data: scatterData.filter(d => d.y === 1),
          backgroundColor: "rgba(76, 175, 80, 0.7)",
          pointRadius: 6
        },
        {
          label: "Non utile",
          data: scatterData.filter(d => d.y === 0),
          backgroundColor: "rgba(244, 67, 54, 0.7)",
          pointRadius: 6
        }
      ]
    },
    options: {
      responsive: true,
      scales: {
        x: {
          title: {
            display: true,
            text: "Score de similarité"
          },
          min: 0,
          max: 1
        },
        y: {
          title: {
            display: true,
            text: "Utilité"
          },
          ticks: {
            callback: function(value) {
              return value === 1 ? 'Utile' : value === 0 ? 'Non utile' : '';
            }
          },
          min: -0.5,
          max: 1.5
        }
      },
      plugins: {
        tooltip: {
          callbacks: {
            label: function(context) {
              return `Score: ${context.parsed.x.toFixed(3)}, ${context.dataset.label}`;
            }
          }
        }
      }
    }
  });
};

onMounted(() => {
  loadData();
});
</script>

<style scoped>
.dashboard {
  padding: 20px;
  background: #f5f5f5;
  min-height: 100vh;
  box-sizing: border-box;
}

h1 {
  text-align:center;
  margin-bottom:30px;
}

/* Ligne principale */
.main-row {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 20px;
}

/* Cartes normales */
.card {
  background:white;
  padding:20px;
  border-radius:15px;
  box-shadow:0 4px 10px rgba(0,0,0,0.1);
  flex: 1 1 400px;
  min-height: 400px;
}

/* Carte spéciale pour le camembert plus petit */
.small-pie-card {
  background:white;
  padding:20px;
  border-radius:15px;
  box-shadow:0 4px 10px rgba(0,0,0,0.1);
  flex: 1 1 400px;
  max-width: 450px; /* Limite la largeur pour le camembert */
}

/* Canvas responsive */
canvas {
  max-width:100%;
  height:300px;
}


</style>