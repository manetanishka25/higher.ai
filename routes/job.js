const express = require('express');
const router = express.Router();

// In-memory store for demo
const jobs = [];

// Create job
router.post('/', (req, res) => {
  const { companyId, title, description, location, requirements } = req.body;
  const id = jobs.length + 1;
  const job = { id, companyId, title, description, location, requirements };
  jobs.push(job);
  res.json(job);
});

// Get all jobs
router.get('/', (req, res) => {
  res.json(jobs);
});

// Get jobs by company
router.get('/company/:companyId', (req, res) => {
  const companyJobs = jobs.filter(j => j.companyId == req.params.companyId);
  res.json(companyJobs);
});

// Get job by ID
router.get('/:id', (req, res) => {
  const job = jobs.find(j => j.id == req.params.id);
  if (!job) return res.status(404).json({ error: 'Job not found' });
  res.json(job);
});

// Update job
router.put('/:id', (req, res) => {
  const job = jobs.find(j => j.id == req.params.id);
  if (!job) return res.status(404).json({ error: 'Job not found' });
  Object.assign(job, req.body);
  res.json(job);
});

// Delete job
router.delete('/:id', (req, res) => {
  const idx = jobs.findIndex(j => j.id == req.params.id);
  if (idx === -1) return res.status(404).json({ error: 'Job not found' });
  jobs.splice(idx, 1);
  res.json({ success: true });
});

module.exports = router;
