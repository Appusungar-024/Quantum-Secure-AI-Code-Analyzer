// script.js
document.addEventListener('DOMContentLoaded', function() {
    const codeTextarea = document.getElementById('code');
    const fileInput = document.getElementById('file');

    fileInput.addEventListener('change', function() {
        if (fileInput.files.length > 0) {
            codeTextarea.disabled = true;
            codeTextarea.placeholder = 'File uploaded, code input disabled';
        } else {
            codeTextarea.disabled = false;
            codeTextarea.placeholder = 'Paste your Python code here...';
        }
    });

    // Syntax highlighting could be added here if needed
});