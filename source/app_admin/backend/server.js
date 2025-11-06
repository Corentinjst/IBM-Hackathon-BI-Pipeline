// server.js
const express = require('express');
const cors = require('cors');
const { initDatabase } = require('./db');
const questionsRoutes = require('./routes/questions');
const dashboardRoutes = require('./routes/dashboard');

require('dotenv').config({ path: '../../.env' });

const app = express();
app.use(cors());
app.use(express.json());

// Routes
app.use('/api/questions', questionsRoutes);
app.use('/api/dashboard', dashboardRoutes);

const PORT = process.env.PORT || 3000;

initDatabase().then(() => {
  app.listen(PORT, () => console.log(`✓ Serveur démarré sur http://localhost:${PORT}`));
});
