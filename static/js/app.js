document.addEventListener('DOMContentLoaded', () => {
  // Tab Navigation
  const tabBtns = document.querySelectorAll('.tab-btn');
  const tabContents = document.querySelectorAll('.tab-content');

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const target = btn.dataset.tab;
      tabBtns.forEach(b => b.classList.remove('active'));
      tabContents.forEach(c => c.classList.remove('active'));

      btn.classList.add('active');
      document.getElementById(target).classList.add('active');

      if (target === 'evaluation-tab') {
        loadEvaluationMetrics();
      }
    });
  });

  const rawInput = document.getElementById('raw-input');
  const redactedOutput = document.getElementById('redacted-output');
  const totalEntitiesEl = document.getElementById('stat-total-entities');
  const execTimeEl = document.getElementById('stat-exec-time');
  const modeBtns = document.querySelectorAll('.mode-btn');

  let currentMode = 'synthetic';
  let typingTimer;

  modeBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      modeBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentMode = btn.dataset.mode;
      processLiveRedaction();
    });
  });

  rawInput.addEventListener('input', () => {
    clearTimeout(typingTimer);
    typingTimer = setTimeout(processLiveRedaction, 300);
  });

  async function processLiveRedaction() {
    const text = rawInput.value;
    if (!text.trim()) {
      redactedOutput.innerHTML = '<span style="color: var(--text-secondary);">Redacted output will appear here live...</span>';
      totalEntitiesEl.textContent = '0';
      execTimeEl.textContent = '0 ms';
      return;
    }

    try {
      const response = await fetch('/api/redact-text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, mode: currentMode })
      });
      const data = await response.json();

      totalEntitiesEl.textContent = data.stats.total;
      execTimeEl.textContent = `${data.execution_ms} ms`;

      let formattedText = data.redacted_text;
      if (data.changes && data.changes.length > 0) {
        data.changes.forEach(chg => {
          const chipHtml = `<span class="pii-chip ${chg.type}" title="Original: ${chg.original}">${chg.replacement}</span>`;
          formattedText = formattedText.replace(chg.replacement, chipHtml);
        });
      }
      redactedOutput.innerHTML = formattedText;
    } catch (err) {
      console.error('Live redaction error:', err);
    }
  }

  document.getElementById('btn-copy').addEventListener('click', () => {
    const text = redactedOutput.innerText;
    navigator.clipboard.writeText(text).then(() => {
      alert('Redacted text copied to clipboard!');
    });
  });

  document.getElementById('btn-load-sample').addEventListener('click', () => {
    rawInput.value = `[TICKET #10492] Customer: Rashi Patil
Email: rashhi.patil@gmail.com, Phone: +91 9876543210
Address: 45 Park Avenue, Block C, Bandra West, Mumbai 400050, India
Govt ID: 324-55-9102, DOB: 14/08/1992, Credit Card: 4532-8910-4421-9018, IP: 192.168.1.104
Company: Acme Solutions Pvt Ltd. Alternate: John Doe (john.doe@example.com, +91 1234567645).`;
    processLiveRedaction();
  });

  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('file-input');
  const fileResult = document.getElementById('file-result');

  dropzone.addEventListener('click', () => fileInput.click());

  dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('dragover');
  });

  dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));

  dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('dragover');
    if (e.dataTransfer.files.length > 0) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener('change', () => {
    if (fileInput.files.length > 0) {
      handleFileUpload(fileInput.files[0]);
    }
  });

  async function handleFileUpload(file) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('mode', currentMode);

    fileResult.style.display = 'block';
    fileResult.innerHTML = '<p>Processing document redaction...</p>';

    try {
      const response = await fetch('/api/redact-file', {
        method: 'POST',
        body: formData
      });
      const data = await response.json();

      if (data.error) {
        fileResult.innerHTML = `<p style="color: var(--danger);">Error: ${data.error}</p>`;
        return;
      }

      fileResult.innerHTML = `
        <div style="background: var(--bg-card); padding: 1.5rem; border-radius: 12px; border: 1px solid var(--border-color); margin-top: 1rem;">
          <h3 style="color: var(--success); margin-bottom: 0.5rem;">🎉 Document Redaction Complete!</h3>
          <p><strong>File Name:</strong> ${data.filename}</p>
          <p><strong>Total PII Entities Redacted:</strong> ${data.total_redactions}</p>
          <p><strong>Processing Time:</strong> ${data.execution_ms} ms</p>
          <br>
          <a href="${data.download_url}" class="btn-primary" download>📥 Download Redacted File (${data.output_filename})</a>
        </div>
      `;
    } catch (err) {
      fileResult.innerHTML = `<p style="color: var(--danger);">Upload failed: ${err.message}</p>`;
    }
  }

  async function loadEvaluationMetrics() {
    try {
      const response = await fetch('/api/evaluation');
      const data = await response.json();

      const overall = data.overall;
      document.getElementById('metric-precision').textContent = `${(overall.Precision * 100).toFixed(1)}%`;
      document.getElementById('metric-recall').textContent = `${(overall.Recall * 100).toFixed(1)}%`;
      document.getElementById('metric-f1').textContent = `${(overall.F1_Score * 100).toFixed(1)}%`;
      document.getElementById('metric-accuracy').textContent = `${(overall.Accuracy * 100).toFixed(1)}%`;

      const tbody = document.getElementById('eval-table-body');
      tbody.innerHTML = '';

      Object.entries(data.per_category).forEach(([cat, stats]) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td><span class="pii-chip ${cat}">${cat}</span></td>
          <td>${stats.TP}</td>
          <td>${stats.FP}</td>
          <td>${stats.FN}</td>
          <td>${(stats.Precision * 100).toFixed(1)}%</td>
          <td>${(stats.Recall * 100).toFixed(1)}%</td>
          <td>${(stats.F1_Score * 100).toFixed(1)}%</td>
          <td>${(stats.Accuracy * 100).toFixed(1)}%</td>
        `;
        tbody.appendChild(tr);
      });
    } catch (err) {
      console.error('Failed to load metrics:', err);
    }
  }
});
