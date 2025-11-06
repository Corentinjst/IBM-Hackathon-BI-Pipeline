// routes/dashboard.js
const express = require('express');
const router = express.Router();
const { getPool } = require('../db');

// READ - toutes les questions
router.get('/', async (req, res) => {
  try {
    const pool = getPool();
    const [rows] = await pool.query('SELECT * FROM support_tickets');
    res.json(rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});


module.exports = router;

