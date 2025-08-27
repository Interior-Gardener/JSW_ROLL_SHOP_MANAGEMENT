function downloadfile() {
    const a = document.createElement('a');
    a.href = "/download/Basic_template.xlsx"; // Correct Flask route
    a.download = 'Basic_template.xlsx';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

// Add loading animation on page load
document.addEventListener('DOMContentLoaded', function () {
    document.querySelector('.container')?.classList.add('loading');
});

// Enhanced file drop functionality with visual feedback
const dropArea = document.querySelector('.drop-area');
const browseBtn = document.querySelector('.btn.browse');
const fileInput = document.getElementById('fileInput');
const filenameDisplay = document.getElementById('filename');

browseBtn?.addEventListener('click', () => fileInput.click());

dropArea?.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropArea.style.borderColor = '#3498db';
    dropArea.style.background = 'rgba(52, 152, 219, 0.1)';
});

dropArea?.addEventListener('dragleave', () => {
    dropArea.style.borderColor = '#bbb';
    dropArea.style.background = 'rgba(255, 255, 255, 0.5)';
});

dropArea?.addEventListener('drop', (e) => {
    e.preventDefault();
    dropArea.style.borderColor = '#bbb';
    dropArea.style.background = 'rgba(255, 255, 255, 0.5)';

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        fileInput.files = files;

        // Show filename
        filenameDisplay.textContent = files[0].name;
    }
});

// Show loading overlay on form submit
document.querySelector('form')?.addEventListener('submit', function () {
    document.getElementById('loading-overlay').style.display = 'flex';
});

// File input filename display
fileInput?.addEventListener('change', function () {
    const fileName = this.files.length > 0 ? this.files[0].name : "No file selected";
    filenameDisplay.textContent = fileName;
});
