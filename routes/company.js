const express = require('express');
const router = express.Router();

// In-memory store for demo
const companies = [];

// Create company
router.post('/', (req, res) => {
  const { name, logoUrl, primaryColor } = req.body;
  const id = companies.length + 1;
  const company = { id, name, logoUrl, primaryColor };
  companies.push(company);
  res.json(company);
});

// Get all companies
router.get('/', (req, res) => {
  res.json(companies);
});

// Get company by ID
router.get('/:id', (req, res) => {
  const company = companies.find(c => c.id == req.params.id);
  if (!company) return res.status(404).json({ error: 'Company not found' });
  res.json(company);
});

module.exports = router;
