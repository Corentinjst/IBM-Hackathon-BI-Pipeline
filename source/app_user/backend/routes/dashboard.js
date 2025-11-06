// routes/dashboard.js
const express = require('express');
const router = express.Router();
const { getPool } = require('../db');

// READ - les 5 questions les plus fréquentes
router.get('/questions', async (req, res) => {
  try {
    const pool = getPool();
    const [rows] = await pool.query(`
      SELECT matched_question_title, COUNT(*) AS count
      FROM feedback
      GROUP BY matched_question_title
      ORDER BY count DESC
      LIMIT 3
    `);
    res.json(rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// POST - Enregistrer le feedback utilisateur (thumbs up/down)
router.post('/feedback', async (req, res) => {
  try {
    const {
      user_query,
      matched_question_id,
      matched_question_title,
      similarity_score,
      was_helpful,
      user_feedback,
      response_time_ms
    } = req.body;

    // Validation : user_query est obligatoire
    if (!user_query) {
      return res.status(400).json({ error: 'user_query est obligatoire' });
    }

    const pool = getPool();
    const [result] = await pool.query(`
      INSERT INTO feedback (
        user_query,
        matched_question_id,
        matched_question_title,
        similarity_score,
        was_helpful,
        user_feedback,
        response_time_ms
      ) VALUES (?, ?, ?, ?, ?, ?, ?)
    `, [
      user_query,
      matched_question_id || null,
      matched_question_title || null,
      similarity_score || null,
      was_helpful,
      user_feedback || null,
      response_time_ms || null
    ]);

    res.status(201).json({
      message: 'Feedback enregistré avec succès',
      id: result.insertId
    });
  } catch (err) {
    console.error('Erreur lors de l\'enregistrement du feedback:', err);
    res.status(500).json({ error: err.message });
  }
});

// POST - Créer un ticket de support
router.post('/support-ticket', async (req, res) => {
  try {
    const {
      user_email,
      user_school,
      user_type,
      question
    } = req.body;

    // Validation : tous les champs sont obligatoires
    if (!user_email || !user_school || !user_type || !question) {
      return res.status(400).json({
        error: 'Tous les champs sont obligatoires (user_email, user_school, user_type, question)'
      });
    }

    // Validation de l'email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(user_email)) {
      return res.status(400).json({ error: 'Format d\'email invalide' });
    }

    const pool = getPool();
    const [result] = await pool.query(`
      INSERT INTO support_tickets (
        user_email,
        user_school,
        user_type,
        question
      ) VALUES (?, ?, ?, ?)
    `, [
      user_email,
      user_school,
      user_type,
      question
    ]);

    res.status(201).json({
      message: 'Ticket de support créé avec succès',
      id: result.insertId
    });
  } catch (err) {
    console.error('Erreur lors de la création du ticket de support:', err);
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;

