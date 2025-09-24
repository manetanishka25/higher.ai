const express = require('express');
const router = express.Router();
const logger = require('../config/logger');

// In-memory store for demo
const jobs = [];

// Create job
router.post('/', (req, res) => {
  try {
    const id = jobs.length + 1;
    const job = {
      id,
      ...req.body,
      applicationForm: {
        requiredFields: req.body.requiredFields || [],
        customFields: req.body.customFields || []
      },
      createdAt: new Date().toISOString()
    };
    
    jobs.push(job);
    
    logger.info('Job created successfully', {
      jobId: job.id,
      title: job.title,
      department: job.department,
      requiredFields: job.applicationForm.requiredFields
    });
    
    res.status(201).json(job);
  } catch (error) {
    logger.error('Error creating job', {
      error: error.message,
      body: req.body
    });
    res.status(400).json({ error: error.message });
  }
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
  try {
    const job = jobs.find(j => j.id == req.params.id);
    if (!job) return res.status(404).json({ error: 'Job not found' });

    // Ensure applicationForm is included
    const jobWithFields = {
      ...job,
      applicationForm: job.applicationForm || {
        requiredFields: [],
        customFields: []
      }
    };
    
    res.json(jobWithFields);
  } catch (error) {
    logger.error('Error fetching job:', { error: error.message, id: req.params.id });
    res.status(500).json({ error: error.message });
  }
});

// Update job
router.put('/:id', (req, res) => {
  try {
    const index = jobs.findIndex(j => j.id == req.params.id);
    if (index === -1) return res.status(404).json({ error: 'Job not found' });
    jobs[index] = { ...jobs[index], ...req.body };
    res.json(jobs[index]);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Delete job
router.delete('/:id', (req, res) => {
  try {
    const index = jobs.findIndex(j => j.id == req.params.id);
    if (index === -1) return res.status(404).json({ error: 'Job not found' });
    jobs.splice(index, 1);
    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
