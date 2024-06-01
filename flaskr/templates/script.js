document.getElementById('bpmForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const bpm = document.getElementById('bpm').value;
    generateSound(bpm);
});

function generateSound(bpm) {
    fetch('/generate_sound', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `bpm=${bpm}`
    })
    .then(response => response.blob())
    .then(blob => {
        const audio = new Audio(URL.createObjectURL(blob));
        audio.play();
    });
}
