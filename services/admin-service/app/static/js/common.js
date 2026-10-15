//
// js/common.js
//

'use strict';

// Atualiza automaticamente o ano exibido no rodapé das páginas.
const currentYear = document.querySelector('[data-current-year]');

if (currentYear) {
    currentYear.textContent = new Date().getFullYear().toString();
}

// Controla a navegação lateral em telas menores.
const dashboardSidebar = document.querySelector(
    '[data-dashboard-sidebar]'
);
const sidebarToggle = document.querySelector('[data-sidebar-toggle]');
const sidebarOverlay = document.querySelector('[data-sidebar-overlay]');

if (dashboardSidebar && sidebarToggle && sidebarOverlay) {
    sidebarToggle.addEventListener('click', () => {
        const isOpen = dashboardSidebar.classList.toggle('is-open');
        sidebarOverlay.classList.toggle('is-visible', isOpen);
        sidebarToggle.setAttribute('aria-expanded', isOpen.toString());
        document.body.classList.toggle('has-open-sidebar', isOpen);
    });

    sidebarOverlay.addEventListener('click', () => {
        dashboardSidebar.classList.remove('is-open');
        sidebarOverlay.classList.remove('is-visible');
        sidebarToggle.setAttribute('aria-expanded', 'false');
        document.body.classList.remove('has-open-sidebar');
    });
}
