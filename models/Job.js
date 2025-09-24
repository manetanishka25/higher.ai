const mongoose = require('mongoose');

const jobSchema = new mongoose.Schema({
  companyId: { type: Number, required: true },
  title: { type: String, required: true },
  department: { type: String, required: true },
  employmentType: { type: String, required: true },
  workMode: { type: String, required: true },
  location: { type: String, required: true },
  description: { type: String, required: true },
  responsibilities: { type: String, required: true },
  requiredQualifications: { type: String, required: true },
  preferredQualifications: String,
  salaryRange: { type: String, required: true },
  benefits: String,
  postingDate: { type: Date, default: Date.now },
  applicationDeadline: Date,
  hiringManager: { type: String, required: true },
  recruiterContact: { type: String, required: true },
  jobId: String,
  equalOpportunityStatement: String,
  approvalStatus: { type: String, default: 'pending' },
  applicationForm: {
    requiredFields: [String],
    customFields: [{
      label: String,
      type: String,
      required: Boolean
    }]
  }
}, { timestamps: true });

module.exports = mongoose.model('Job', jobSchema);
