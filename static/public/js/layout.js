// Atualiza o ano no rodapé
document.addEventListener('DOMContentLoaded', function() {
  const footerYear = document.getElementById("footer-year");
  if (footerYear) {
    footerYear.textContent = new Date().getFullYear();
  }
});

// Corrige o menu toggle
function toggleMenu() {
  const menu = document.getElementById('mobile-menu');
  if (menu) {
    menu.classList.toggle('show');
  }
}

function closeMenu() {
  const menu = document.getElementById('mobile-menu');
  if (menu) {
    menu.classList.remove('show');
  }
}

// Evento do botão
document.addEventListener('DOMContentLoaded', function() {
  const menuToggle = document.getElementById('menu-toggle');
  if (menuToggle) {
    menuToggle.addEventListener('click', toggleMenu);
  }
});
