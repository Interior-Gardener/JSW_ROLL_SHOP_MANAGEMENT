document.getElementById('rollerForm').addEventListener('submit', async function (e) {
  e.preventDefault();

  const data = {
    rollNumber: document.getElementById('rollNumber').value,
    status: document.getElementById('status').value,
    minDiameter: parseFloat(document.getElementById('minDiameter').value),
    maxDiameter: parseFloat(document.getElementById('maxDiameter').value),
    currentDiameter: parseFloat(document.getElementById('currentDiameter').value),
    location: document.getElementById('location').value
  };

  try {
    const response = await fetch('http://localhost:3000/api/rollers', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });

    if (response.ok) {
      alert('Roller data submitted successfully!');
      document.getElementById('rollerForm').reset();
    } else {
      alert('Error submitting data.');
    }
  } catch (error) {
    console.error('Submission failed:', error);
    alert('Server connection error.');
  }
});
// Add shake animation for invalid fields
function animateShake(element) {
  element.style.borderColor = 'var(--danger-color)';
  element.style.animation = 'shake 0.5s';

  setTimeout(() => {
    element.style.animation = '';
  }, 500);
}

// Add shake animation keyframes
document.head.insertAdjacentHTML('beforeend', `
    <style>
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
            20%, 40%, 60%, 80% { transform: translateX(5px); }
        }
    </style>
`);
