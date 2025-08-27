function downloadfile() {
    const a = document.createElement('a');
    a.href = "Basic_template.xlsx";
    a.download = 'Basic_template.xlsx';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

// Add loading animation on page load
        document.addEventListener('DOMContentLoaded', function() {
            document.querySelector('.container').classList.add('loading');
        });

        // Enhanced file drop functionality with visual feedback
        const dropArea = document.querySelector('.drop-area');
        const fileInput = document.getElementById('fileInput');
        const browseBtn = document.querySelector('.btn.browse');

        browseBtn.addEventListener('click', () => fileInput.click());

        dropArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropArea.style.borderColor = '#3498db';
            dropArea.style.background = 'rgba(52, 152, 219, 0.1)';
        });

        dropArea.addEventListener('dragleave', () => {
            dropArea.style.borderColor = '#bbb';
            dropArea.style.background = 'rgba(255, 255, 255, 0.5)';
        });

        dropArea.addEventListener('drop', (e) => {
            e.preventDefault();
            dropArea.style.borderColor = '#bbb';
            dropArea.style.background = 'rgba(255, 255, 255, 0.5)';
            // Handle file drop logic here
        });