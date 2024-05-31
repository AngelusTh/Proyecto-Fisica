document.addEventListener("DOMContentLoaded", () => {
    const socket = io();
    const form = document.getElementById('parabola-form');
    const queryInput = document.getElementById('query');
    const resultEl = document.getElementById('result');

    queryInput.addEventListener('input', () => {
        const query = queryInput.value;
        if (query) {
            socket.emit('calculate', { query });
        }
    });

    socket.on('result', data => {
        resultEl.textContent = data.resultado;
    });
});
