document.querySelectorAll('.classe-card').forEach(card => {
    card.addEventListener('click', function () {
      this.classList.toggle('active');
    });
  });