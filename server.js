require('dotenv').config();
const express = require('express');
// const connectDB = require('./config/database'); // Commented out MongoDB
const bodyParser = require('body-parser');
const cors = require('cors');
const path = require('path');
const logger = require('./config/logger');

// Connect to MongoDB - Commented out for now
// connectDB();

const companyRoutes = require('./routes/company');
const jobRoutes = require('./routes/job');
const applicationRoutes = require('./routes/application');

const app = express();
app.use(cors());
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, 'public')));
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

app.use('/api/company', companyRoutes);
app.use('/api/job', jobRoutes);
app.use('/api/application', applicationRoutes);

const PORT = process.env.PORT || 4000;

// Error handling middleware
app.use((err, req, res, next) => {
  logger.error('Express error:', {
    message: err.message,
    stack: err.stack,
    path: req.path,
    method: req.method,
    body: req.body,
    query: req.query,
    ip: req.ip
  });
  
  res.status(500).json({ 
    error: 'Something went wrong!',
    message: err.message,
    requestId: req.id
  });
});

app.listen(PORT, () => {
  logger.info(`Server running on port ${PORT}`);
});
