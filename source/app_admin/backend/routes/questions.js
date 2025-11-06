// routes/questions.js
const express = require('express');
const router = express.Router();
const { getPool } = require('../db');

// Champs autorisés
const allowedFields = [
  'title',
  'content',
  'date',
  'post_type',
  'langues',
  'thematiques',
  'utilisateurs',
  'ecoles',
  'status'
];

// CREATE
router.post('/', async (req, res) => {
  try {
    const pool = getPool();
    const payload = {};
    for (const f of allowedFields) {
      if (req.body[f] !== undefined) payload[f] = req.body[f];
    }

    if (Object.keys(payload).length === 0) {
      return res.status(400).json({ error: 'Aucun champ valide fourni' });
    }

    const cols = Object.keys(payload).join(', ');
    const placeholders = Object.keys(payload).map(() => '?').join(', ');
    const values = Object.values(payload);

    const [result] = await pool.query(
      `INSERT INTO questions (${cols}) VALUES (${placeholders})`,
      values
    );

    res.status(201).json({
      id: result.insertId,
      ...payload,
      message: 'Question créée avec succès'
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// READ - toutes les questions
router.get('/', async (req, res) => {
  try {
    const pool = getPool();
    const [rows] = await pool.query('SELECT * FROM questions ORDER BY created_at DESC');
    res.json(rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// READ - une question par ID
router.get('/:id', async (req, res) => {
  try {
    const pool = getPool();
    const [rows] = await pool.query('SELECT * FROM questions WHERE id = ?', [req.params.id]);
    if (rows.length === 0) {
      return res.status(404).json({ error: 'Question non trouvée' });
    }
    res.json(rows[0]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// UPDATE
router.put('/:id', async (req, res) => {
  try {
    const pool = getPool();
    const updates = [];
    const values = [];

    for (const f of allowedFields) {
      if (req.body[f] !== undefined) {
        updates.push(`${f} = ?`);
        values.push(req.body[f]);
      }
    }

    if (updates.length === 0) {
      return res.status(400).json({ error: 'Aucun champ valide à mettre à jour' });
    }

    values.push(req.params.id);
    const sql = `UPDATE questions SET ${updates.join(', ')} WHERE id = ?`;
    const [result] = await pool.query(sql, values);

    if (result.affectedRows === 0) {
      return res.status(404).json({ error: 'Question non trouvée' });
    }

    res.json({ id: req.params.id, message: 'Question mise à jour' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// DELETE
router.delete('/:id', async (req, res) => {
  try {
    const pool = getPool();
    const [result] = await pool.query('DELETE FROM questions WHERE id = ?', [req.params.id]);
    if (result.affectedRows === 0) {
      return res.status(404).json({ error: 'Question non trouvée' });
    }
    res.json({ message: 'Question supprimée avec succès' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
