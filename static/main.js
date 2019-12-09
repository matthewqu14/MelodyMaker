const fileAudio = document.getElementById('fileAudio');
const player1 = document.getElementById('player1');

fileAudio.addEventListener('change', function(e) {
const file = e.target.files[0];
const url = URL.createObjectURL(file);
player1.src = url;
});