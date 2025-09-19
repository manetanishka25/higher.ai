const express = require('express');
const router = express.Router();

// In-memory store for demo
const applications = [];

// Submit application
router.post('/', (req, res) => {
  const { jobId, name, email, resumeUrl } = req.body;
  const id = applications.length + 1;
  const application = { id, jobId, name, email, resumeUrl };
  applications.push(application);
  res.json(application);
});

// Get all applications
router.get('/', (req, res) => {
  res.json(applications);
});

// Get applications for a job
router.get('/job/:jobId', (req, res) => {
  const jobApps = applications.filter(a => a.jobId == req.params.jobId);
  res.json(jobApps);
});

module.exports = router;
