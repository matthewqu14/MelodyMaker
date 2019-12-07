var slider = document.getElementById("bpm");
var output = document.getElementById("bpm_num");
var f = document.getElementById("flash");
output.innerHTML = slider.value;
setInterval(function() {
    f.style.display = (f.style.display == 'none' ? '' : 'none');
}, 500 / (parseFloat(output.innerHTML) / 60.0));
slider.oninput = function() {
    output.innerHTML = slider.value;
    setInterval(function() {
        f.style.display = (f.style.display == 'none' ? '' : 'none');
    }, 500 / (parseFloat(output.innerHTML) / 60.0));
}

const recorder = document.getElementById('recorder');
const player = document.getElementById('player');

recorder.addEventListener('change', function(e) {
const file = e.target.files[0];
const url = URL.createObjectURL(file);
// Do something with the audio file.
player.src = url;
});