document.addEventListener('DOMContentLoaded', (event) => {
    const ctx = document.getElementById('trajectoryChart').getContext('2d');
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Movimiento Parabólico',
                data: [],
                borderColor: '#00a8ff',
                borderWidth: 2,
                fill: false,
                pointRadius: 0
            }]
        },
        options: {
            scales: {
                x: {
                    type: 'linear',
                    position: 'bottom',
                    title: {
                        display: true,
                        text: 'Distancia (m)',
                        color: '#dcdde1'
                    },
                    ticks: {
                        beginAtZero: true,
                        color: '#dcdde1'
                    },
                    grid: {
                        color: '#353b48'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Altura (m)',
                        color: '#dcdde1'
                    },
                    ticks: {
                        beginAtZero: true,
                        color: '#dcdde1'
                    },
                    grid: {
                        color: '#353b48'
                    }
                }
            },
            animation: {
                duration: 0
            },
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        color: '#dcdde1'
                    }
                }
            }
        }
    });

    const calculate = () => {
        const initialHeight = parseFloat(document.getElementById('initialHeight').value);
        const velocity = parseFloat(document.getElementById('velocity').value);
        const angle = parseFloat(document.getElementById('angle').value);
        const gravity = parseFloat(document.getElementById('gravity').value);

        const angleRadians = angle * (Math.PI / 180);
        const timeOfFlight = (velocity * Math.sin(angleRadians) + Math.sqrt(Math.pow(velocity * Math.sin(angleRadians), 2) + 2 * gravity * initialHeight)) / gravity;
        const totalTime = Math.ceil(timeOfFlight * 100) / 100;
        const maxHeight = initialHeight + Math.pow(velocity * Math.sin(angleRadians), 2) / (2 * gravity);
        const distance = (velocity * Math.cos(angleRadians)) * totalTime;

        let dataPoints = [];
        for (let t = 0; t <= totalTime; t += 0.01) {
            const x = velocity * t * Math.cos(angleRadians);
            const y = initialHeight + (velocity * t * Math.sin(angleRadians)) - (0.5 * gravity * t * t);
            if (y >= 0) {
                dataPoints.push({ x: x.toFixed(2), y: y.toFixed(2) });
            }
        }

        chart.data.labels = dataPoints.map(point => point.x);
        chart.data.datasets[0].data = dataPoints.map(point => point.y);
        chart.update();

        document.getElementById('distanceResult').innerText = `Distancia Recorrida: ${distance.toFixed(2)} m`;
        document.getElementById('maxHeightResult').innerText = `Altura Máxima: ${maxHeight.toFixed(2)} m`;
        document.getElementById('totalTimeResult').innerText = `Tiempo Total: ${totalTime.toFixed(2)} s`;
    }

    document.querySelectorAll('input').forEach(input => {
        input.addEventListener('input', calculate);
    });

    calculate();
});
