// ===== TOPS - JAVASCRIPT LIMPO E ESPECÍFICO =====

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar funcionalidades dos tops
    initTops();
    
    // Adicionar efeitos de hover
    initHoverEffects();
    
    // Adicionar funcionalidade de busca
    initSearchFunctionality();
    
    // Garantir alinhamento das colunas
    fixColumnAlignment();
    
    // Adicionar listener para redimensionamento
    window.addEventListener('resize', function() {
        setTimeout(fixColumnAlignment, 100);
    });
});

function initTops() {
    // Adicionar classes para melhor estilização
    const tables = document.querySelectorAll('.tops-table');
    tables.forEach(table => {
        table.classList.add('tops-table-enhanced');
        
        // Adicionar tooltips para badges
        const badges = table.querySelectorAll('.tops-badge');
        badges.forEach(badge => {
            if (badge.textContent.trim()) {
                badge.title = badge.textContent.trim();
            }
        });
    });
}

function initHoverEffects() {
    const tableRows = document.querySelectorAll('.tops-table tbody tr');
    
    tableRows.forEach((row, index) => {
        // Adicionar delay de animação baseado na posição
        row.style.animationDelay = `${index * 0.1}s`;
        
        // Adicionar efeito de destaque ao hover
        row.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px) scale(1.01)';
            this.style.zIndex = '10';
        });
        
        row.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
            this.style.zIndex = '1';
        });
        
        // Adicionar efeito de clique
        row.addEventListener('click', function() {
            // Remover destaque de outras linhas
            tableRows.forEach(r => r.classList.remove('selected-row'));
            // Adicionar destaque à linha clicada
            this.classList.add('selected-row');
        });
    });
}

function initSearchFunctionality() {
    // Adicionar campo de busca se não existir
    const tableContainers = document.querySelectorAll('.tops-table-container');
    
    tableContainers.forEach(container => {
        const table = container.querySelector('.tops-table-responsive');
        if (table && !container.querySelector('.tops-search')) {
            addSearchField(container, table);
        }
    });
}

function addSearchField(container, table) {
    const searchHTML = `
        <div class="tops-search mb-4">
            <div class="tops-search-input">
                <i class="fas fa-search"></i>
                <input type="text" placeholder="Buscar jogador..." id="search-${Date.now()}" autocomplete="off">
                <button type="button" id="clear-search-${Date.now()}">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="tops-search-info">
                <small>Digite o nome do jogador para filtrar os resultados</small>
            </div>
        </div>
    `;
    
    container.insertAdjacentHTML('afterbegin', searchHTML);
    
    const searchInput = container.querySelector('input[type="text"]');
    const clearButton = container.querySelector('button[type="button"]');
    const tbody = table.querySelector('tbody');
    const searchInfo = container.querySelector('.tops-search-info');
    
    if (searchInput && tbody) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            
            searchTimeout = setTimeout(() => {
                const searchTerm = this.value.toLowerCase().trim();
                
                // Verificar e corrigir problemas de display antes da busca
                fixDisplayIssues(container);
                
                const rows = tbody.querySelectorAll('tr');
                let visibleCount = 0;
                
                // Se o termo de busca estiver vazio, mostrar todas as linhas
                if (searchTerm === '') {
                    rows.forEach((row, index) => {
                        // Remover qualquer CSS inline que possa estar causando problemas
                        row.removeAttribute('style');
                        row.style.display = 'table-row';
                        row.style.opacity = '1';
                        row.style.visibility = 'visible';
                        row.style.height = '';
                        row.style.color = '';
                        row.style.animation = 'fadeInUp 0.3s ease';
                        row.style.animationDelay = `${index * 0.05}s`;
                        visibleCount++;
                    });
                } else {
                    // Filtrar linhas baseado no termo de busca
                    rows.forEach((row, index) => {
                        const playerName = row.querySelector('td:nth-child(2)')?.textContent.toLowerCase() || '';
                        const clanName = row.querySelector('td:nth-child(3)')?.textContent.toLowerCase() || '';
                        const className = row.querySelector('td:nth-child(6)')?.textContent.toLowerCase() || '';
                        
                        const matches = playerName.includes(searchTerm) || 
                                      clanName.includes(searchTerm) || 
                                      className.includes(searchTerm);
                        
                        if (matches) {
                            row.style.display = 'table-row';
                            row.style.opacity = '1';
                            row.style.visibility = 'visible';
                            row.style.height = '';
                            row.style.color = '';
                            row.style.animation = 'fadeInUp 0.3s ease';
                            row.style.animationDelay = `${index * 0.05}s`;
                            visibleCount++;
                        } else {
                            row.style.display = 'none';
                        }
                    });
                }
                
                // Atualizar informações de busca
                updateSearchInfo(searchInfo, visibleCount, rows.length, searchTerm);
                
                // Mostrar/esconder botão de limpar
                if (searchTerm) {
                    clearButton.style.display = 'block';
                } else {
                    clearButton.style.display = 'none';
                }
                
                // Verificação final para garantir que tudo está correto
                if (searchTerm === '') {
                    setTimeout(() => {
                        fixDisplayIssues(container);
                    }, 100);
                }
            }, 300);
        });
        
        // Funcionalidade do botão limpar
        clearButton.addEventListener('click', function() {
            resetSearch(container);
        });
        
        // Adicionar listener para tecla Escape
        searchInput.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                resetSearch(container);
            }
        });
        
        // Foco automático no campo de busca
        searchInput.focus();
    }
}

function updateSearchInfo(searchInfo, visibleCount, totalCount, searchTerm) {
    if (searchTerm && searchTerm.length > 0) {
        searchInfo.innerHTML = `
            <small style="color: #e6c77d;">
                <i class="fas fa-search" style="color: #d1a44f;"></i>
                ${visibleCount} de ${totalCount} resultados encontrados para "${searchTerm}"
            </small>
        `;
    } else {
        searchInfo.innerHTML = `
            <small style="color: rgba(230, 199, 125, 0.7);">
                <i class="fas fa-info-circle" style="color: #e6c77d;"></i>
                Digite o nome do jogador para filtrar os resultados
            </small>
        `;
    }
}

// Função para resetar completamente a busca
function resetSearch(container) {
    const searchInput = container.querySelector('input[type="text"]');
    const clearButton = container.querySelector('button[type="button"]');
    const tbody = container.querySelector('tbody');
    const searchInfo = container.querySelector('.tops-search-info');
    
    if (searchInput && tbody) {
        searchInput.value = '';
        
        // Mostrar todas as linhas
        const rows = tbody.querySelectorAll('tr');
        rows.forEach((row, index) => {
            // Remover qualquer CSS inline que possa estar causando problemas
            row.removeAttribute('style');
            row.style.display = 'table-row';
            row.style.opacity = '1';
            row.style.visibility = 'visible';
            row.style.height = '';
            row.style.color = '';
            row.style.animation = 'fadeInUp 0.3s ease';
            row.style.animationDelay = `${index * 0.05}s`;
        });
        
        // Atualizar informações
        updateSearchInfo(searchInfo, rows.length, rows.length, '');
        
        // Esconder botão limpar
        if (clearButton) {
            clearButton.style.display = 'none';
        }
        
        // Focar no campo
        searchInput.focus();
    }
}

function fixColumnAlignment() {
    const tables = document.querySelectorAll('.tops-table');
    
    tables.forEach(table => {
        const headers = table.querySelectorAll('thead th');
        const firstRow = table.querySelector('tbody tr');
        
        if (headers.length > 0 && firstRow) {
            const cells = firstRow.querySelectorAll('td');
            
            // Aplicar alinhamento específico para cada coluna
            if (headers[0] && cells[0]) {
                headers[0].style.textAlign = 'center';
                cells[0].style.textAlign = 'center';
            }
            
            if (headers[1] && cells[1]) {
                headers[1].style.textAlign = 'left';
                cells[1].style.textAlign = 'left';
            }
            
            if (headers[2] && cells[2]) {
                headers[2].style.textAlign = 'left';
                cells[2].style.textAlign = 'left';
            }
            
            if (headers[3] && cells[3]) {
                headers[3].style.textAlign = 'center';
                cells[3].style.textAlign = 'center';
            }
            
            if (headers[4] && cells[4]) {
                headers[4].style.textAlign = 'center';
                cells[4].style.textAlign = 'center';
            }
            
            if (headers[5] && cells[5]) {
                headers[5].style.textAlign = 'center';
                cells[5].style.textAlign = 'center';
            }
        }
        
        // Aplicar alinhamento para todas as células da tabela
        const allCells = table.querySelectorAll('tbody td');
        allCells.forEach((cell, index) => {
            const columnIndex = index % 6; // 6 colunas
            
            switch(columnIndex) {
                case 0: // Ranking
                    cell.style.textAlign = 'center';
                    break;
                case 1: // Jogador
                    cell.style.textAlign = 'left';
                    break;
                case 2: // Clã
                    cell.style.textAlign = 'left';
                    break;
                case 3: // PvP
                    cell.style.textAlign = 'center';
                    break;
                case 4: // Nível
                    cell.style.textAlign = 'center';
                    break;
                case 5: // Classe
                    cell.style.textAlign = 'center';
                    break;
            }
        });
        
        // Correção específica para o primeiro lugar
        fixFirstPlaceAlignment(table);
    });
}

function fixFirstPlaceAlignment(table) {
    const firstRow = table.querySelector('tbody tr:nth-child(1)');
    if (firstRow) {
        const cells = firstRow.querySelectorAll('td');
        
        // Garantir que a primeira célula (ranking) esteja centralizada
        if (cells[0]) {
            cells[0].style.textAlign = 'center';
            cells[0].style.display = 'flex';
            cells[0].style.alignItems = 'center';
            cells[0].style.justifyContent = 'center';
            
            const badge = cells[0].querySelector('.tops-badge');
            if (badge) {
                badge.style.margin = '0 auto';
                badge.style.display = 'inline-block';
            }
        }
        
        // Garantir que a segunda célula (jogador) esteja alinhada à esquerda
        if (cells[1]) {
            cells[1].style.textAlign = 'left';
            const flex = cells[1].querySelector('.tops-flex');
            if (flex) {
                flex.style.display = 'flex';
                flex.style.alignItems = 'center';
                flex.style.gap = '8px';
                flex.style.textAlign = 'left';
            }
        }
        
        // Garantir que a terceira célula (clã) esteja alinhada à esquerda
        if (cells[2]) {
            cells[2].style.textAlign = 'left';
            const flex = cells[2].querySelector('.tops-flex');
            if (flex) {
                flex.style.display = 'flex';
                flex.style.alignItems = 'center';
                flex.style.gap = '8px';
                flex.style.textAlign = 'left';
            }
        }
        
        // Garantir que as outras células estejam centralizadas
        for (let i = 3; i < cells.length; i++) {
            if (cells[i]) {
                cells[i].style.textAlign = 'center';
                const badge = cells[i].querySelector('.tops-badge, .tops-text-muted');
                if (badge) {
                    badge.style.margin = '0 auto';
                    badge.style.display = 'inline-block';
                }
            }
        }
    }
}

// Função para verificar e corrigir problemas de display
function fixDisplayIssues(container) {
    const tbody = container.querySelector('tbody');
    if (tbody) {
        const rows = tbody.querySelectorAll('tr');
        rows.forEach(row => {
            // Verificar se a linha está visível
            const computedStyle = window.getComputedStyle(row);
            if (computedStyle.display === 'none') {
                row.removeAttribute('style');
                row.style.display = 'table-row';
            }
        });
    }
}

// Adicionar estilos CSS dinâmicos
const dynamicStyles = `
    .selected-row {
        background: linear-gradient(135deg, rgba(230, 199, 125, 0.2), rgba(155, 117, 48, 0.2)) !important;
        border-left: 4px solid #e6c77d !important;
    }
    
    .tops-search {
        background: linear-gradient(135deg, rgba(53, 47, 35, 0.95), rgba(40, 35, 25, 0.95));
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(230, 199, 125, 0.2);
        margin-bottom: 20px;
    }
    
    .tops-search-input {
        display: flex;
        align-items: center;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 25px;
        padding: 12px 20px;
        border: 1px solid rgba(230, 199, 125, 0.3);
        transition: all 0.3s ease;
    }
    
    .tops-search-input:focus-within {
        border-color: #e6c77d;
        box-shadow: 0 0 0 0.2rem rgba(230, 199, 125, 0.25);
    }
    
    .tops-search-input i {
        color: #e6c77d;
        margin-right: 10px;
    }
    
    .tops-search-input input {
        flex: 1;
        background: transparent;
        border: none;
        color: #fff;
        font-size: 14px;
        outline: none;
    }
    
    .tops-search-input input::placeholder {
        color: rgba(255, 255, 255, 0.5);
    }
    
    .tops-search-input button {
        background: none;
        border: none;
        color: #e6c77d;
        cursor: pointer;
        padding: 5px;
        border-radius: 50%;
        transition: all 0.3s ease;
        display: none;
    }
    
    .tops-search-input button:hover {
        background: rgba(230, 199, 125, 0.2);
    }
    
    .tops-search-info {
        margin-top: 10px;
        text-align: center;
    }
    
    .tops-search-info small {
        color: rgba(255, 255, 255, 0.6);
        font-size: 12px;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .tops-table tbody tr {
        animation: fadeInUp 0.6s ease forwards;
    }
`;

const styleSheet = document.createElement('style');
styleSheet.textContent = dynamicStyles;
document.head.appendChild(styleSheet); 