const slider = document.getElementById("bpm");
const output = document.getElementById("bpm_num");
const f = document.getElementById("flash");
output.innerHTML = slider.value;

setInterval(function() {
    f.style.display = (f.style.display == 'none' ? '' : 'none');
    }, 500 / (parseFloat(output.innerHTML) / 60.0));
    slider.oninput = function() {
    output.innerHTML = slider.value;
    setInterval(function() {
        f.style.display = (f.style.display == 'none' ? '' : 'none');
    }, 500 / (parseFloat(output.innerHTML) / 60.0));
};

const fileAudio = document.getElementById('fileAudio');
const player1 = document.getElementById('player1');

fileAudio.addEventListener('change', function(e) {
const file = e.target.files[0];
const url = URL.createObjectURL(file);
// Do something with the audio file.
player1.src = url;
});