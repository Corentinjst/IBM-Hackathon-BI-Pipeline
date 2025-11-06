// db.js
const mysql = require('mysql2/promise');
require('dotenv').config({ path: '../../.env' });

const dbConfig = {
  host: process.env.DB_HOST || 'localhost',
  user: process.env.DB_USER || '',
  password: process.env.DB_PASSWORD || '',
  database: process.env.DB_NAME || 'help_center',
  port: parseInt(process.env.DB_PORT || '3306', 10),
  waitForConnections: (process.env.DB_WAIT_FOR_CONNECTIONS || 'true') === 'true',
  connectionLimit: parseInt(process.env.DB_CONNECTION_LIMIT || '10', 10),
  queueLimit: parseInt(process.env.DB_QUEUE_LIMIT || '0', 10),
};

let pool;

async function initDatabase() {
  if (!pool) {
    pool = mysql.createPool(dbConfig);
    try {
      const conn = await pool.getConnection();
      await conn.ping();
      conn.release();
      console.log('✓ Connecté à MariaDB');
    } catch (err) {
      console.error('Erreur de connexion à la base de données :', err);
      process.exit(1);
    }
  }
  return pool;
}

function getPool() {
  if (!pool) throw new Error('La base de données n’est pas initialisée. Appeler initDatabase() avant.');
  return pool;
}

module.exports = { initDatabase, getPool };
