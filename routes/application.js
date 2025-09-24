const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const logger = require('../config/logger');
const { getFieldLabel } = require('../utils/fieldUtils');

// Create uploads directory if it doesn't exist
const uploadsDir = path.join(__dirname, '../uploads');
if (!fs.existsSync(uploadsDir)){
    fs.mkdirSync(uploadsDir);
}

// Configure multer with error handling
const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, uploadsDir)
    },
    filename: function (req, file, cb) {
        const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
        cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
    }
});

const fileFilter = (req, file, cb) => {
    const allowedTypes = ['.pdf', '.doc', '.docx'];
    const ext = path.extname(file.originalname).toLowerCase();
    if (allowedTypes.includes(ext)) {
        cb(null, true);
    } else {
        cb(new Error('Invalid file type. Only PDF, DOC, and DOCX files are allowed.'));
    }
};

const upload = multer({
    storage: storage,
    fileFilter: fileFilter,
    limits: {
        fileSize: 5 * 1024 * 1024 // 5MB limit
    }
}).single('resumeFile');

const router = express.Router();

// In-memory store for demo
const applications = [];

// Update the post route with better error handling
router.post('/upload', (req, res) => {
    upload(req, res, async function(err) {
        if (err instanceof multer.MulterError) {
            logger.error('File upload error:', {
                type: 'MulterError',
                code: err.code,
                field: err.field,
                originalField: req.body, // Log the received fields
                message: err.message,
                stack: err.stack
            });
            return res.status(400).json({ 
                error: 'File upload error',
                details: err.message,
                code: err.code
            });
        } else if (err) {
            logger.error('Unknown upload error:', {
                error: err.message,
                stack: err.stack
            });
            return res.status(400).json({ error: err.message });
        }

        if (!req.file) {
            logger.warn('No file uploaded');
            return res.status(400).json({ error: 'Please upload a resume file' });
        }

        try {
            // Get job configuration
            const job = await Job.findById(req.body.jobId);
            if (!job) {
                return res.status(404).json({ error: 'Job not found' });
            }

            // Validate required fields
            const missingFields = [];
            if (job.applicationForm?.requiredFields) {
                job.applicationForm.requiredFields.forEach(field => {
                    if (!req.body[field]) {
                        missingFields.push(getFieldLabel(field));
                    }
                });
            }

            if (missingFields.length) {
                return res.status(400).json({
                    error: `Missing required fields: ${missingFields.join(', ')}`
                });
            }

            const application = {
                id: applications.length + 1,
                jobId: req.body.jobId,
                fullName: req.body.fullName,
                email: req.body.email,
                phone: req.body.phone,
                location: req.body.location,
                workAuth: req.body.workAuth,
                currentRole: req.body.currentRole,
                experience: req.body.experience,
                linkedin: req.body.linkedin,
                resumeUrl: `/uploads/${req.file.filename}`,
                expectedSalary: req.body.expectedSalary,
                noticePeriod: req.body.noticePeriod,
                coverLetter: req.body.coverLetter,
                portfolio: req.body.portfolio,
                preferredLocation: req.body.preferredLocation,
                referral: req.body.referral,
                status: 'applied', // Change from 'new' to 'applied'
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString(),
                customFields: Object.entries(req.body)
                    .filter(([key]) => key.startsWith('custom_'))
                    .map(([key, value]) => ({
                        field: key.replace('custom_', ''),
                        value
                    }))
            };

            applications.push(application);
            
            logger.info('Application submitted successfully', {
                applicationId: application.id,
                jobId: application.jobId,
                candidate: application.fullName,
                status: application.status
            });
            
            res.status(201).json(application);
        } catch (error) {
            logger.error('Application processing error:', {
                error: error.message,
                stack: error.stack,
                body: req.body
            });
            res.status(400).json({ error: error.message });
        }
    });
});

// Update application status
router.patch('/:id/status', (req, res) => {
  try {
    const { status } = req.body;
    const application = applications.find(a => a.id == req.params.id);
    
    if (!application) {
      logger.warn(`Application not found with id: ${req.params.id}`);
      return res.status(404).json({ error: 'Application not found' });
    }
    
    application.status = status;
    application.updatedAt = new Date().toISOString();
    
    logger.info('Application status updated', {
      applicationId: application.id,
      newStatus: status,
      candidate: application.fullName
    });
    
    res.json(application);
  } catch (error) {
    logger.error('Error updating application status:', {
      error: error.message,
      applicationId: req.params.id
    });
    res.status(500).json({ error: error.message });
  }
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
