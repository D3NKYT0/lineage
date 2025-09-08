document.addEventListener("DOMContentLoaded", function() {
    // Obtém o elemento pelo ID
    var cpfField = document.getElementById('id_cpf') || document.getElementById('cpf');
    
    if (cpfField) {
        cpfField.addEventListener('input', function(event) {
            var value = event.target.value;

            // Remove todos os caracteres não numéricos
            value = value.replace(/\D/g, '');

            // Adiciona a formatação de CPF
            if (value.length > 11) {
                value = value.slice(0, 11); // Limita a 11 dígitos
            }

            // Adiciona a formatação de pontos e hífen
            var formattedValue = value;
            if (value.length > 9) {
                formattedValue = value.slice(0, 3) + '.' + value.slice(3, 6) + '.' + value.slice(6, 9) + '-' + value.slice(9);
            } else if (value.length > 6) {
                formattedValue = value.slice(0, 3) + '.' + value.slice(3, 6) + '.' + value.slice(6);
            } else if (value.length > 3) {
                formattedValue = value.slice(0, 3) + '.' + value.slice(3);
            }

            event.target.value = formattedValue;
        });
    }
});
