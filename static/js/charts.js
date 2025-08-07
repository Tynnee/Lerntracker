document.addEventListener('DOMContentLoaded', function () {
    // Finde alle Canvas-Elemente mit der Klasse 'progress-chart'
    const canvases = document.querySelectorAll('canvas.progress-chart');
    canvases.forEach(canvas => {
        const ctx = canvas.getContext('2d');
        const progress = parseFloat(canvas.dataset.progress);
        const goalId = canvas.dataset.goalId;

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Fortschritt'],
                datasets: [{
                    label: 'Fortschritt (%)',
                    data: [progress],
                    backgroundColor: '#28a745',
                    borderColor: '#1e7e34',
                    borderWidth: 1
                }]
            },
            options: {
                indexAxis: 'y',
                scales: {
                    x: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Fortschritt (%)'
                        }
                    },
                    y: {
                        display: false
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    });
});