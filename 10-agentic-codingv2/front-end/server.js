/**
 * Express Server for Agentic RAG Frontend
 * Serves static files and handles routing
 */

require('dotenv').config();
const express = require('express');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 9091;
const API_URL = process.env.API_URL || 'http://localhost:9090';

// Serve static files from public directory
app.use(express.static(path.join(__dirname, 'public')));

// API configuration endpoint for frontend
app.get('/config', (req, res) => {
    res.json({
        apiUrl: API_URL
    });
});

// Route handlers for different pages
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.get('/chat', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'chat.html'));
});

app.get('/about', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'about.html'));
});

app.get('/contact', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'contact.html'));
});

// 404 handler
app.use((req, res) => {
    res.status(404).sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Start server
app.listen(PORT, () => {
    console.log(`\x1b[36m%s\x1b[0m`, '='.repeat(60));
    console.log(`\x1b[32m%s\x1b[0m`, '🚀 Agentic RAG Frontend Server');
    console.log(`\x1b[36m%s\x1b[0m`, '='.repeat(60));
    console.log(`\x1b[33m%s\x1b[0m`, `📡 Server running on: http://localhost:${PORT}`);
    console.log(`\x1b[33m%s\x1b[0m`, `🔗 Backend API: ${API_URL}`);
    console.log(`\x1b[36m%s\x1b[0m`, '='.repeat(60));
});
