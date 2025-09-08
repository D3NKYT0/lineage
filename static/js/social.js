/**
 * JavaScript para a Rede Social
 * Melhora a interatividade dos botões de ação do formulário de posts
 */

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar funcionalidades do social
    initSocialFeatures();
});

function initSocialFeatures() {
    // Inicializar botões de ação
    initActionButtons();
    
    // Inicializar contadores
    initCounters();
    
    // Inicializar previews
    initPreviews();
    
    // Inicializar validações
    initValidations();
    
    // Inicializar menus suspensos
    initDropdownMenus();
}

function initActionButtons() {
    // Adicionar efeitos visuais aos botões de ação
    const actionButtons = document.querySelectorAll('.action-button');
    
    actionButtons.forEach(button => {
        // Efeito de clique
        button.addEventListener('click', function(e) {
            const buttonType = this.getAttribute('data-type');
            
            // Adicionar classe de loading temporariamente
            this.classList.add('loading');
            
            // Remover loading após 500ms
            setTimeout(() => {
                this.classList.remove('loading');
            }, 500);
            
            // Efeito de ripple
            createRippleEffect(e, this);
            
            // Efeito visual para botões de mídia
            if (buttonType === 'image' || buttonType === 'video') {
                // O efeito será tratado pelo evento change do input
            }
        });
        
        // Efeito de hover
        button.addEventListener('mouseenter', function() {
            // Hover effect without sound
        });
        
        // Feedback visual ao selecionar arquivo (apenas para image e video)
        const buttonType = button.getAttribute('data-type');
        if (buttonType === 'image' || buttonType === 'video') {
            const input = button.parentElement.querySelector('input');
            if (input) {
                input.addEventListener('change', function() {
                    const button = this.parentElement.querySelector('.action-button');
                    if (this.files && this.files.length > 0) {
                        button.style.borderColor = '#28a745';
                        button.style.backgroundColor = '#f8fff9';
                        
                        // Mostrar nome do arquivo selecionado
                        const fileName = this.files[0].name;
                        const hint = button.querySelector('.action-hint');
                        if (hint) {
                            hint.textContent = fileName.length > 20 ? fileName.substring(0, 20) + '...' : fileName;
                            hint.style.color = '#28a745';
                        }
                    }
                });
            }
        }
    });
}

function createRippleEffect(event, element) {
    const ripple = document.createElement('span');
    const rect = element.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;
    
    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';
    ripple.classList.add('ripple');
    
    element.appendChild(ripple);
    
    setTimeout(() => {
        ripple.remove();
    }, 600);
}



function initCounters() {
    const contentTextarea = document.querySelector('#id_content');
    
    if (contentTextarea) {
        const charCount = document.getElementById('char-count');
        const charCountMobile = document.getElementById('char-count-mobile');
        const hashtagCount = document.getElementById('hashtag-count');
        const hashtagCountMobile = document.getElementById('hashtag-count-mobile');
        
        function updateCounts() {
            const content = contentTextarea.value;
            const charCountValue = content.length;
            const maxLength = 1000;
            
            // Update character count
            if (charCount) charCount.textContent = charCountValue;
            if (charCountMobile) charCountMobile.textContent = charCountValue;
            
            // Update hashtag count from content
            const hashtags = content.match(/#\w+/g) || [];
            const hashtagCountValue = hashtags.length;
            
            if (hashtagCount) hashtagCount.textContent = hashtagCountValue;
            if (hashtagCountMobile) hashtagCountMobile.textContent = hashtagCountValue;
            
            // Mudar cor baseado no limite
            if (charCountValue > maxLength * 0.9) {
                if (charCount) charCount.parentElement.classList.add('text-warning');
                if (charCountMobile) charCountMobile.parentElement.classList.add('text-warning');
            } else {
                if (charCount) charCount.parentElement.classList.remove('text-warning');
                if (charCountMobile) charCountMobile.parentElement.classList.remove('text-warning');
            }
            
            if (charCountValue > maxLength * 0.95) {
                if (charCount) charCount.parentElement.classList.add('text-danger');
                if (charCountMobile) charCountMobile.parentElement.classList.add('text-danger');
            } else {
                if (charCount) charCount.parentElement.classList.remove('text-danger');
                if (charCountMobile) charCountMobile.parentElement.classList.remove('text-danger');
            }
        }
        
        contentTextarea.addEventListener('input', updateCounts);
        updateCounts(); // Contagem inicial
    }
}

function initPreviews() {
    // Preview de imagem
    const imageInput = document.querySelector('#id_image');
    if (imageInput) {
        imageInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    showMediaPreview(e.target.result, file.name, 'image');
                };
                reader.readAsDataURL(file);
            }
        });
    }
    
    // Preview de vídeo
    const videoInput = document.querySelector('#id_video');
    if (videoInput) {
        videoInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    showMediaPreview(e.target.result, file.name, 'video');
                };
                reader.readAsDataURL(file);
            }
        });
    }
}

function showMediaPreview(src, fileName, type) {
    const preview = document.getElementById('media-preview');
    const previewMobile = document.getElementById('media-preview-mobile');
    const content = document.getElementById('preview-content');
    const contentMobile = document.getElementById('preview-content-mobile');
    
    let html = '';
    if (type === 'image') {
        html = `<img src="${src}" alt="Preview" class="img-fluid rounded" style="max-height: 100px;">`;
    } else if (type === 'video') {
        html = `<video controls class="img-fluid rounded" style="max-height: 100px;"><source src="${src}"></video>`;
    }
    
    html += `<div class="mt-2"><small class="text-muted">${fileName}</small></div>`;
    
    if (content) content.innerHTML = html;
    if (contentMobile) contentMobile.innerHTML = html;
    if (preview) preview.style.display = 'block';
    if (previewMobile) previewMobile.style.display = 'block';
}



function clearMedia() {
    const imageInput = document.querySelector('#id_image');
    const videoInput = document.querySelector('#id_video');
    
    if (imageInput) imageInput.value = '';
    if (videoInput) videoInput.value = '';
    
    const preview = document.getElementById('media-preview');
    const previewMobile = document.getElementById('media-preview-mobile');
    
    if (preview) preview.style.display = 'none';
    if (previewMobile) previewMobile.style.display = 'none';
    
    // Resetar botões
    resetActionButtons();
}





function clearMediaMobile() {
    clearMedia();
}



function resetActionButtons() {
    const actionButtons = document.querySelectorAll('.action-button');
    actionButtons.forEach(button => {
        button.style.borderColor = '#e9ecef';
        button.style.backgroundColor = 'white';
        
        const hint = button.querySelector('.action-hint');
        if (hint) {
            const type = button.getAttribute('data-type');
            switch(type) {
                case 'image':
                    hint.textContent = 'JPG, PNG, GIF';
                    break;
                case 'video':
                    hint.textContent = 'MP4, AVI, MOV';
                    break;
            }
            hint.style.color = '#6c757d';
        }
    });
}

function initDropdownMenus() {
    // Inicializar menus suspensos de mídia
    const mediaDropdowns = document.querySelectorAll('#mediaDropdown, #mediaDropdownMobile');
    
    mediaDropdowns.forEach(dropdown => {
        // Adicionar efeito visual ao abrir o menu
        dropdown.addEventListener('click', function() {
            this.classList.add('active');
        });
        
        // Remover classe ativa quando o menu fechar
        dropdown.addEventListener('blur', function() {
            setTimeout(() => {
                this.classList.remove('active');
            }, 200);
        });
    });
    
    // Adicionar feedback visual para inputs de arquivo
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            if (this.files && this.files.length > 0) {
                // Mostrar notificação de arquivo selecionado
                const fileName = this.files[0].name;
                const fileType = this.id === 'id_image' ? 'imagem' : 'vídeo';
                showNotification(`${fileType} selecionada: ${fileName}`, 'success');
                
                // Atualizar preview se necessário
                updateMediaPreview(this);
            }
        });
    });
}

function updateMediaPreview(input) {
    const file = input.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    const isImage = input.id === 'id_image';
    
    reader.onload = function(e) {
        const previewId = isImage ? 'preview-content' : 'preview-content';
        const previewContainer = document.getElementById('media-preview');
        const previewMobileContainer = document.getElementById('media-preview-mobile');
        
        if (previewContainer) {
            previewContainer.style.display = 'block';
            const previewContent = document.getElementById(previewId);
            if (previewContent) {
                if (isImage) {
                    previewContent.innerHTML = `<img src="${e.target.result}" class="img-fluid rounded" style="max-height: 200px;">`;
                } else {
                    previewContent.innerHTML = `<video src="${e.target.result}" controls class="img-fluid rounded" style="max-height: 200px;"></video>`;
                }
            }
        }
        
        if (previewMobileContainer) {
            previewMobileContainer.style.display = 'block';
            const previewMobileContent = document.getElementById('preview-content-mobile');
            if (previewMobileContent) {
                if (isImage) {
                    previewMobileContent.innerHTML = `<img src="${e.target.result}" class="img-fluid rounded" style="max-height: 150px;">`;
                } else {
                    previewMobileContent.innerHTML = `<video src="${e.target.result}" controls class="img-fluid rounded" style="max-height: 150px;"></video>`;
                }
            }
        }
    };
    
    reader.readAsDataURL(file);
}

function initValidations() {
    const form = document.getElementById('post-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            const content = document.querySelector('#id_content');
            if (!content.value.trim()) {
                e.preventDefault();
                showNotification('Por favor, escreva algo antes de publicar!', 'warning');
                content.focus();
                return false;
            }
            
            // Validar tamanho de arquivos
            const imageInput = document.querySelector('#id_image');
            const videoInput = document.querySelector('#id_video');
            
            if (imageInput && imageInput.files[0]) {
                const fileSize = imageInput.files[0].size / (1024 * 1024); // MB
                if (fileSize > 5) {
                    e.preventDefault();
                    showNotification('A imagem deve ter no máximo 5MB!', 'error');
                    return false;
                }
            }
            
            if (videoInput && videoInput.files[0]) {
                const fileSize = videoInput.files[0].size / (1024 * 1024); // MB
                if (fileSize > 50) {
                    e.preventDefault();
                    showNotification('O vídeo deve ter no máximo 50MB!', 'error');
                    return false;
                }
            }
        });
    }
}



function showNotification(message, type = 'info') {
    // Criar notificação toast
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    // Adicionar ao container de toasts
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '1055';
        document.body.appendChild(toastContainer);
    }
    
    toastContainer.appendChild(toast);
    
    // Mostrar toast
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remover após ser escondido
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

// Adicionar estilos CSS dinâmicos para o efeito ripple
const style = document.createElement('style');
style.textContent = `
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.6);
        transform: scale(0);
        animation: ripple-animation 0.6s linear;
        pointer-events: none;
    }
    
    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    .action-button {
        position: relative;
        overflow: hidden;
    }
`;
document.head.appendChild(style);
