let currentSlide = 0;
const slides = document.querySelectorAll('.slide');

function showSlide(nextIndex) {
  if (nextIndex === currentSlide) return;

  const current = slides[currentSlide];
  const next = slides[nextIndex];

  // Slide current out to left
  current.classList.remove('active');
  current.classList.add('previous');

  // Slide next in from right
  next.classList.add('active');

  // After animation ends, clean up previous slide
  setTimeout(() => {
    current.classList.remove('previous');
  }, 500); // match CSS transition time

  currentSlide = nextIndex;
}

function nextSlide() {
  let nextIndex = (currentSlide + 1) % slides.length;
  showSlide(nextIndex);
}

function prevSlide() {
  let prevIndex = (currentSlide - 1 + slides.length) % slides.length;
  showSlide(prevIndex);
}

// Auto slide every 3 seconds
setInterval(nextSlide, 3000);

// Initialize first slide active on page load
showSlide(0);