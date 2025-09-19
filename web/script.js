document.addEventListener('DOMContentLoaded', () => {
  // Elements
  const baseUrlInput = document.getElementById('baseUrl');
  const apiKeyInput = document.getElementById('apiKey');
  const fileInput = document.getElementById('fileInput');
  const textInput = document.getElementById('textInput');
  const rawChk = document.getElementById('rawChk');
  const rawChkText = document.getElementById('rawChkText');
  const parseFileBtn = document.getElementById('parseFileBtn');
  const parseTextBtn = document.getElementById('parseTextBtn');
  const statusEl = document.getElementById('status');
  const outputEl = document.getElementById('output');
  const copyBtn = document.getElementById('copyBtn');
  const downloadBtn = document.getElementById('downloadBtn');
  
  // File upload UI enhancement
  const fileUpload = document.querySelector('.file-upload');
  const fileLabel = fileUpload.querySelector('p');
  const originalText = fileLabel.textContent;
  
  fileInput.addEventListener('change', () => {
    if (fileInput.files.length > 0) {
      fileLabel.textContent = `Selected: ${fileInput.files[0].name}`;
    } else {
      fileLabel.textContent = originalText;
    }
  });
  
  // Drag and drop
  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    fileUpload.addEventListener(eventName, preventDefaults, false);
  });
  
  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }
  
  ['dragenter', 'dragover'].forEach(eventName => {
    fileUpload.addEventListener(eventName, highlight, false);
  });
  
  ['dragleave', 'drop'].forEach(eventName => {
    fileUpload.addEventListener(eventName, unhighlight, false);
  });
  
  function highlight() {
    fileUpload.style.borderColor = 'var(--primary)';
    fileUpload.style.backgroundColor = 'rgba(74, 111, 165, 0.05)';
  }
  
  function unhighlight() {
    fileUpload.style.borderColor = 'var(--border)';
    fileUpload.style.backgroundColor = 'transparent';
  }
  
  fileUpload.addEventListener('drop', (e) => {
    fileInput.files = e.dataTransfer.files;
    if (fileInput.files.length > 0) {
      fileLabel.textContent = `Selected: ${fileInput.files[0].name}`;
    }
  });
  
  // Parse functions
  parseFileBtn.addEventListener('click', async function () {
    if (!fileInput.files.length) {
      showStatus('Please select a file to upload.', 'error');
      return;
    }
    await parseResume(true);
  });
  
  parseTextBtn.addEventListener('click', async () => {
    if (!textInput.value.trim()) {
      showStatus('Please enter some text first', 'error');
      return;
    }
    await parseResume(false);
  });
  
  async function parseResume(isFile) {
    const baseUrl = baseUrlInput.value.trim();
    const apiKey = apiKeyInput.value.trim();
    
    if (!baseUrl) {
      showStatus('Please enter API base URL', 'error');
      return;
    }
    
    const btn = isFile ? parseFileBtn : parseTextBtn;
    const includeRaw = isFile ? rawChk.checked : rawChkText.checked;
    
    showStatus('', '');
    btn.classList.add('loading');
    btn.disabled = true;
    
    try {
      const formData = new FormData();
      
      if (isFile) {
        formData.append('file', fileInput.files[0]);
      } else {
        formData.append('text', textInput.value);
      }
      
      formData.append('include_raw_text', includeRaw);
      
      const response = await fetch(`${baseUrl}/parse`, {
        method: 'POST',
        headers: {
          'X-API-Key': apiKey
        },
        body: formData
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API Error (${response.status}): ${errorText}`);
      }
      
      const result = await response.json();
      outputEl.textContent = JSON.stringify(result, null, 2);
      showStatus('Resume parsed successfully!', 'success');
      
      copyBtn.disabled = false;
      downloadBtn.disabled = false;
      
    } catch (error) {
      console.error(error);
      showStatus(`Error: ${error.message}`, 'error');
    } finally {
      btn.classList.remove('loading');
      btn.disabled = false;
    }
  }
  
  // Copy and download functions
  copyBtn.addEventListener('click', () => {
    navigator.clipboard.writeText(outputEl.textContent)
      .then(() => {
        const originalText = copyBtn.textContent;
        copyBtn.innerHTML = '<i class="fas fa-check"></i> Copied!';
        setTimeout(() => {
          copyBtn.innerHTML = '<i class="fas fa-copy"></i> Copy JSON';
        }, 2000);
      })
      .catch(err => {
        showStatus('Failed to copy: ' + err, 'error');
      });
  });
  
  downloadBtn.addEventListener('click', () => {
    try {
      const content = outputEl.textContent;
      const blob = new Blob([content], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      
      const a = document.createElement('a');
      a.href = url;
      a.download = 'parsed_resume.json';
      document.body.appendChild(a);
      a.click();
      
      // Cleanup
      setTimeout(() => {
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }, 0);
      
    } catch (error) {
      showStatus(`Download error: ${error.message}`, 'error');
    }
  });
  
  function showStatus(message, type) {
    if (!message) {
      statusEl.style.display = 'none';
      return;
    }
    
    statusEl.textContent = message;
    statusEl.className = 'status';
    
    if (type) {
      statusEl.classList.add(type);
    }
    
    statusEl.style.display = 'block';
  }
});
