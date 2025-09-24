const getFieldLabel = (field) => {
  const labels = {
    github: 'GitHub Profile',
    portfolio: 'Portfolio/Projects',
    leetcode: 'LeetCode Profile',
    linkedin: 'LinkedIn Profile',
    stackoverflow: 'Stack Overflow Profile',
    kaggle: 'Kaggle Profile'
  };
  return labels[field] || field;
};

const getFieldType = (field) => {
  const urlFields = ['github', 'portfolio', 'linkedin', 'leetcode', 'stackoverflow', 'kaggle'];
  return urlFields.includes(field) ? 'url' : 'text';
};

module.exports = {
  getFieldLabel,
  getFieldType
};
