// server.js
const express = require('express');
const cors = require('cors');
const { initDatabase } = require('./db');
const dashboardRoutes = require('./routes/dashboard');
// const autreTableRoutes = require('./routes/autreTable'); // plus tard

require('dotenv').config({ path: '../../.env' });

const app = express();
app.use(cors());
app.use(express.json());

app.use('/api/dashboard', dashboardRoutes);

const PORT = process.env.USER_PORT || 3000;

initDatabase().then(() => {
  app.listen(PORT, () => console.log(`✓ [USER] Serveur démarré sur http://localhost:${PORT}`));
});
