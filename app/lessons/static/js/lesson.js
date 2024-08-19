document.addEventListener('DOMContentLoaded', function() {
    const playbackSpeedSelect = document.getElementById('playback-speed');
    const audioElements = document.querySelectorAll('audio');

    playbackSpeedSelect.addEventListener('change', function() {
        const speed = this.value;
        audioElements.forEach(audio => {
            audio.playbackRate = parseFloat(speed);
        });
    });

    document.querySelectorAll('.play-pause').forEach(button => {
        button.addEventListener('click', function() {
            const audioId = this.dataset.target;
            const audio = document.getElementById(audioId);
            if (audio.paused) {
                audio.play();
                this.innerHTML = '<i class="bi bi-pause-fill"></i>';
            } else {
                audio.pause();
                this.innerHTML = '<i class="bi bi-play-fill"></i>';
            }
        });
    });
});
