// Cart Modal Management - Fixed for Multiple Opens
document.addEventListener('DOMContentLoaded', function() {
    
    // Get all modals and buttons
    const modals = document.querySelectorAll('.modal');
    const viewItemsButtons = document.querySelectorAll('.btn-view-items');
    
    // Function to open modal by ID
    function openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            // Reset modal state first
            modal.classList.remove('fade', 'show', 'hide', 'closed');
            modal.style.display = 'block';
            modal.style.opacity = '0';
            
            // Force reflow
            modal.offsetHeight;
            
            // Add show classes
            modal.classList.add('show', 'fade');
            modal.style.opacity = '1';
            
            // Add body class
            document.body.classList.add('modal-open');
            
            // Remove any backdrop interference
            const backdrops = document.querySelectorAll('.modal-backdrop');
            backdrops.forEach(backdrop => {
                backdrop.style.display = 'none';
                backdrop.style.zIndex = '-1';
            });
            
            console.log('Modal opened:', modalId);
        }
    }
    
    // Function to close modal
    function closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            // Remove show classes
            modal.classList.remove('show', 'fade');
            modal.style.display = 'none';
            modal.style.opacity = '0';
            
            // Remove body class
            document.body.classList.remove('modal-open');
            
            // Reset modal state
            modal.classList.remove('fade', 'show', 'hide', 'closed');
            
            // Remove any backdrop
            const backdrops = document.querySelectorAll('.modal-backdrop');
            backdrops.forEach(backdrop => {
                backdrop.style.display = 'none';
                backdrop.style.zIndex = '-1';
            });
            
            console.log('Modal closed:', modalId);
        }
    }
    
    // Add event listeners to all "Ver Itens" buttons
    viewItemsButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Get modal ID from data-bs-target
            const modalTarget = this.getAttribute('data-bs-target');
            if (modalTarget) {
                const modalId = modalTarget.replace('#', '');
                openModal(modalId);
            }
        });
    });
    
    // Add event listeners to all close buttons
    const closeButtons = document.querySelectorAll('[data-bs-dismiss="modal"], .btn-close');
    closeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Find the modal this button belongs to
            const modal = this.closest('.modal');
            if (modal) {
                closeModal(modal.id);
            }
        });
    });
    
    // Close modal when clicking outside
    modals.forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                closeModal(this.id);
            }
        });
    });
    
    // Close modal with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal.show');
            if (openModal) {
                closeModal(openModal.id);
            }
        }
    });
    
    // Override Bootstrap modal if it exists
    if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
        const originalShow = bootstrap.Modal.prototype.show;
        const originalHide = bootstrap.Modal.prototype.hide;
        
        bootstrap.Modal.prototype.show = function() {
            // Call original show
            originalShow.call(this);
            
            // Ensure modal is properly shown
            const modalElement = this._element;
            if (modalElement) {
                modalElement.classList.add('show');
                modalElement.style.display = 'block';
                modalElement.style.opacity = '1';
                document.body.classList.add('modal-open');
            }
        };
        
        bootstrap.Modal.prototype.hide = function() {
            // Call original hide
            originalHide.call(this);
            
            // Ensure modal is properly hidden and can be reopened
            setTimeout(() => {
                const modalElement = this._element;
                if (modalElement) {
                    modalElement.classList.remove('show', 'fade');
                    modalElement.style.display = 'none';
                    modalElement.style.opacity = '0';
                    document.body.classList.remove('modal-open');
                    
                    // Reset state
                    modalElement.classList.remove('fade', 'show', 'hide', 'closed');
                }
            }, 150);
        };
    }
    
    // Debug: Log found elements
    console.log('Found modals:', modals.length);
    console.log('Found view items buttons:', viewItemsButtons.length);
    console.log('Found close buttons:', closeButtons.length);
});
