// Admin Custom JavaScript

document.addEventListener('DOMContentLoaded', function() {
    
    // Melhorar campos de tradução
    function enhanceTranslationFields() {
        const translationInlines = document.querySelectorAll('.inline-group');
        translationInlines.forEach(function(inline) {
            if (inline.querySelector('select[name*="language"]')) {
                inline.classList.add('translation-inline');
                
                // Adicionar tooltips para campos de idioma
                const languageSelects = inline.querySelectorAll('select[name*="language"]');
                languageSelects.forEach(function(select) {
                    select.classList.add('form-select');
                    select.style.width = '100px';
                });
                
                // Melhorar campos de texto
                const textInputs = inline.querySelectorAll('input[type="text"], textarea');
                textInputs.forEach(function(input) {
                    input.classList.add('form-control');
                    if (input.tagName === 'TEXTAREA') {
                        input.style.width = '400px';
                        input.style.minHeight = '60px';
                    } else {
                        input.style.width = '300px';
                    }
                });
            }
        });
    }
    
    // Melhorar campos de busca
    function enhanceSearchFields() {
        const searchInputs = document.querySelectorAll('input[name="q"], input[type="search"]');
        searchInputs.forEach(function(input) {
            input.classList.add('search-field');
            input.placeholder = input.placeholder || 'Buscar...';
        });
    }
    
    // Melhorar filtros
    function enhanceFilters() {
        const filterSelects = document.querySelectorAll('.filter-field select, .filter-field input');
        filterSelects.forEach(function(select) {
            select.classList.add('filter-field');
        });
    }
    
    // Melhorar campos de data
    function enhanceDateFields() {
        const dateInputs = document.querySelectorAll('input[type="date"], input[type="datetime-local"]');
        dateInputs.forEach(function(input) {
            input.classList.add('date-field');
        });
    }
    
    // Melhorar campos de checkbox
    function enhanceCheckboxes() {
        const checkboxes = document.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(function(checkbox) {
            checkbox.classList.add('form-check-input');
        });
    }
    
    // Melhorar campos de select
    function enhanceSelects() {
        const selects = document.querySelectorAll('select');
        selects.forEach(function(select) {
            if (!select.classList.contains('form-select')) {
                select.classList.add('form-select');
            }
        });
    }
    
    // Melhorar campos de formulário
    function enhanceFormFields() {
        const inputs = document.querySelectorAll('input[type="text"], input[type="email"], input[type="password"], input[type="number"]');
        inputs.forEach(function(input) {
            if (!input.classList.contains('form-control') && !input.classList.contains('search-field')) {
                input.classList.add('form-control');
            }
        });
    }
    
    // Adicionar tooltips
    function addTooltips() {
        const tooltipElements = document.querySelectorAll('[data-tooltip]');
        tooltipElements.forEach(function(element) {
            element.classList.add('admin-tooltip');
        });
    }
    
    // Melhorar ações em massa
    function enhanceBulkActions() {
        const actionSelect = document.querySelector('select[name="action"]');
        if (actionSelect) {
            actionSelect.classList.add('form-select');
            actionSelect.style.width = '200px';
        }
        
        const actionButton = document.querySelector('input[type="submit"][name="index"]');
        if (actionButton) {
            actionButton.classList.add('btn', 'btn-primary');
            actionButton.style.marginLeft = '10px';
        }
    }
    
    // Melhorar campos de status
    function enhanceStatusFields() {
        const statusElements = document.querySelectorAll('.field-status, .field-is_active, .field-is_published');
        statusElements.forEach(function(element) {
            const value = element.textContent.trim();
            if (value === 'True' || value === 'Sim' || value === 'Ativo') {
                element.innerHTML = '<span class="status-field status-active">Ativo</span>';
            } else if (value === 'False' || value === 'Não' || value === 'Inativo') {
                element.innerHTML = '<span class="status-field status-inactive">Inativo</span>';
            } else if (value === 'Pendente') {
                element.innerHTML = '<span class="status-field status-pending">Pendente</span>';
            }
        });
    }
    
    // Melhorar campos de preço
    function enhancePriceFields() {
        const priceElements = document.querySelectorAll('.field-price, .field-valor, .field-total_pago');
        priceElements.forEach(function(element) {
            const value = element.textContent.trim();
            if (value && !isNaN(parseFloat(value))) {
                const formattedValue = parseFloat(value).toLocaleString('pt-BR', {
                    style: 'currency',
                    currency: 'BRL'
                });
                element.innerHTML = '<span class="price-field">' + formattedValue + '</span>';
            }
        });
    }
    
    // Melhorar campos de quantidade
    function enhanceQuantityFields() {
        const quantityElements = document.querySelectorAll('.field-quantidade, .field-amount, .field-count');
        quantityElements.forEach(function(element) {
            element.classList.add('quantity-field');
        });
    }
    
    // Melhorar campos de data/hora
    function enhanceDateTimeFields() {
        const datetimeElements = document.querySelectorAll('.field-created_at, .field-updated_at, .field-data, .field-date');
        datetimeElements.forEach(function(element) {
            element.classList.add('datetime-field');
        });
    }
    
    // Melhorar campos de usuário
    function enhanceUserFields() {
        const userElements = document.querySelectorAll('.field-user, .field-author, .field-created_by');
        userElements.forEach(function(element) {
            element.classList.add('user-field');
        });
    }
    
    // Melhorar campos de descrição
    function enhanceDescriptionFields() {
        const descriptionElements = document.querySelectorAll('.field-description, .field-descricao, .field-summary');
        descriptionElements.forEach(function(element) {
            element.classList.add('description-field');
        });
    }
    
    // Melhorar campos de imagem
    function enhanceImageFields() {
        const imageElements = document.querySelectorAll('img[src*="media"], img[src*="static"]');
        imageElements.forEach(function(img) {
            img.classList.add('image-preview');
        });
    }
    
    // Melhorar campos de raridade
    function enhanceRarityFields() {
        const rarityElements = document.querySelectorAll('.field-rarity');
        rarityElements.forEach(function(element) {
            const value = element.textContent.trim().toLowerCase();
            let rarityClass = 'rarity-common';
            
            if (value === 'rare') {
                rarityClass = 'rarity-rare';
            } else if (value === 'epic') {
                rarityClass = 'rarity-epic';
            } else if (value === 'legendary') {
                rarityClass = 'rarity-legendary';
            }
            
            element.innerHTML = '<span class="' + rarityClass + '">' + element.textContent + '</span>';
        });
    }
    
    // Auto-save para campos de tradução
    function setupAutoSave() {
        const translationInputs = document.querySelectorAll('.translation-inline input, .translation-inline textarea');
        let saveTimeout;
        
        translationInputs.forEach(function(input) {
            input.addEventListener('input', function() {
                clearTimeout(saveTimeout);
                saveTimeout = setTimeout(function() {
                    // Aqui você pode implementar auto-save se necessário
                    console.log('Auto-save triggered for:', input.name);
                }, 2000);
            });
        });
    }
    
    // Melhorar navegação
    function enhanceNavigation() {
        // Adicionar breadcrumbs se não existirem
        const breadcrumb = document.querySelector('.breadcrumbs');
        if (!breadcrumb) {
            const content = document.querySelector('#content');
            if (content) {
                const title = document.querySelector('h1');
                if (title) {
                    const breadcrumbDiv = document.createElement('div');
                    breadcrumbDiv.className = 'breadcrumbs';
                    breadcrumbDiv.innerHTML = '<a href="/admin/">Admin</a> > ' + title.textContent;
                    content.insertBefore(breadcrumbDiv, content.firstChild);
                }
            }
        }
    }
    
    // Melhorar responsividade
    function enhanceResponsiveness() {
        // Adicionar classes responsivas
        const tables = document.querySelectorAll('.results');
        tables.forEach(function(table) {
            table.classList.add('table-responsive');
        });
        
        // Melhorar formulários em telas pequenas
        if (window.innerWidth < 768) {
            const forms = document.querySelectorAll('form');
            forms.forEach(function(form) {
                form.classList.add('mobile-form');
            });
        }
    }
    
    // Inicializar todas as melhorias
    function initAdminEnhancements() {
        enhanceTranslationFields();
        enhanceSearchFields();
        enhanceFilters();
        enhanceDateFields();
        enhanceCheckboxes();
        enhanceSelects();
        enhanceFormFields();
        addTooltips();
        enhanceBulkActions();
        enhanceStatusFields();
        enhancePriceFields();
        enhanceQuantityFields();
        enhanceDateTimeFields();
        enhanceUserFields();
        enhanceDescriptionFields();
        enhanceImageFields();
        enhanceRarityFields();
        setupAutoSave();
        enhanceNavigation();
        enhanceResponsiveness();
    }
    
    // Executar melhorias
    initAdminEnhancements();
    
    // Re-executar em mudanças dinâmicas (para AJAX)
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                initAdminEnhancements();
            }
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    // Melhorar performance em scroll
    let scrollTimeout;
    window.addEventListener('scroll', function() {
        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(function() {
            // Otimizações durante scroll
        }, 100);
    });
    
    // Melhorar acessibilidade
    function enhanceAccessibility() {
        // Adicionar labels para campos sem label
        const inputs = document.querySelectorAll('input:not([id*="id_"])');
        inputs.forEach(function(input) {
            if (!input.labels || input.labels.length === 0) {
                const label = document.createElement('label');
                label.textContent = input.placeholder || input.name;
                label.setAttribute('for', input.id);
                input.parentNode.insertBefore(label, input);
            }
        });
        
        // Melhorar navegação por teclado
        document.addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.key === 's') {
                e.preventDefault();
                const saveButton = document.querySelector('input[type="submit"][value="Salvar"]');
                if (saveButton) {
                    saveButton.click();
                }
            }
        });
    }
    
    enhanceAccessibility();
});
