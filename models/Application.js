const mongoose = require('mongoose');

const applicationSchema = new mongoose.Schema({
  jobId: { type: mongoose.Schema.Types.ObjectId, ref: 'Job', required: true },
  name: { type: String, required: true },
  email: { type: String, required: true },
  resumeUrl: { type: String, required: true },
  status: { type: String, default: 'new' }
}, { timestamps: true });

module.exports = mongoose.model('Application', applicationSchema);
