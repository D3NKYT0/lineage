document.addEventListener('DOMContentLoaded', function() {
    const calendarEl = document.getElementById('custom-calendar');
    if (!calendarEl) {
        console.error(TRANSLATIONS.calendarNotFound);
        return;
    }

    // Inicializa o modal
    const eventDetailsModal = new bootstrap.Modal(document.getElementById('eventDetailsModal'));

    const calendar = new FullCalendar.Calendar(calendarEl, {
        locale: 'pt-br',
        initialView: 'dayGridMonth',
        themeSystem: 'bootstrap',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        buttonText: TRANSLATIONS.buttonText,
        views: {
            dayGridMonth: {
                titleFormat: { year: 'numeric', month: 'long' }
            },
            timeGridWeek: {
                titleFormat: { year: 'numeric', month: 'long', day: '2-digit' }
            },
            timeGridDay: {
                titleFormat: { year: 'numeric', month: 'long', day: '2-digit' }
            }
        },
        selectable: true,
        editable: true,
        height: 'auto',
        contentHeight: 'auto',
        dayMaxEventRows: 5,
        eventTimeFormat: {
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
        },
        events: {
            url: GET_EVENT_URL,
            failure: function(error) {
                console.error(TRANSLATIONS.loadEventsError, error);
            }
        },
        eventClick: function(info) {
            // Formata as datas
            const startDate = new Date(info.event.start).toLocaleDateString('pt-BR');
            const endDate = new Date(info.event.end).toLocaleDateString('pt-BR');

            // Atualiza o conteúdo do modal
            document.getElementById('eventTitle').textContent = info.event.title;
            document.getElementById('eventStart').textContent = startDate;
            document.getElementById('eventEnd').textContent = endDate;

            // Mostra o modal
            eventDetailsModal.show();
        }
    });
    
    calendar.render();

    // Força uma atualização do layout após a renderização inicial
    setTimeout(() => {
        calendar.updateSize();
    }, 100);

    // Atualiza o tamanho quando a janela for redimensionada
    window.addEventListener('resize', function() {
        calendar.updateSize();
    });
}); 