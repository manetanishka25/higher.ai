const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const path = require('path');

const companyRoutes = require('./routes/company');
const jobRoutes = require('./routes/job');
const applicationRoutes = require('./routes/application');

const app = express();
app.use(cors());
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, 'public')));

app.use('/api/company', companyRoutes);
app.use('/api/job', jobRoutes);
app.use('/api/application', applicationRoutes);

const PORT = process.env.PORT || 4000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
