//webkitURL is deprecated but nevertheless
URL = window.URL || window.webkitURL;

var gumStream; 						//stream from getUserMedia()
var recorder; 						//WebAudioRecorder object
var input; 							//MediaStreamAudioSourceNode  we'll be recording
var encodeAfterRecord = true;       // when to encode

// shim for AudioContext when it's not avb.
var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext; //new audio context to help us record

var recordButton = document.getElementById("recordButton");
var stopButton = document.getElementById("stopButton");
var uploadButton = document.getElementById("uploadButton");
const player2 = document.getElementById('player2');

//add events to those 2 buttons
recordButton.addEventListener("click", startRecording);
stopButton.addEventListener("click", stopRecording);
uploadButton.addEventListener("click", uploadRecording);

function startRecording() {
    console.log("startRecording() called");

    /*
        Simple constraints object, for more advanced features see
        https://addpipe.com/blog/audio-constraints-getusermedia/
    */

    var constraints = {audio: true, video: false}

    /*
    	We're using the standard promise based getUserMedia()
    	https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia
	*/

    navigator.mediaDevices.getUserMedia(constraints).then(function (stream) {
        console.log("getUserMedia() success, stream created, initializing WebAudioRecorder...");

        /*
            create an audio context after getUserMedia is called
            sampleRate might change after getUserMedia is called, like it does on macOS when recording through AirPods
            the sampleRate defaults to the one set in your OS for your playback device

        */
        audioContext = new AudioContext();

        //assign to gumStream for later use
        gumStream = stream;

        /* use the stream */
        input = audioContext.createMediaStreamSource(stream);

        //stop the input from playing back through the speakers
        //input.connect(audioContext.destination)

        recorder = new WebAudioRecorder(input, {
            workerDir: "../static/", // must end with slash
            encoding: 'wav',
            numChannels: 2, //2 is the default, mp3 encoding supports only 2
            onEncoderLoading: function (recorder, encoding) {
                // show "loading encoder..." display
                console.log("Loading " + encoding + " encoder...");
            },
            onEncoderLoaded: function (recorder, encoding) {
                // hide "loading encoder..." display
                console.log(encoding + " encoder loaded");
            }
        });

        recorder.onComplete = function (recorder, blob) {
            console.log("Encoding complete");
            player2.src = URL.createObjectURL(blob);
        }

        recorder.setOptions({
            timeLimit: 120,
            encodeAfterRecord: encodeAfterRecord,
            ogg: {quality: 0.5},
            mp3: {bitRate: 160}
        });

        //start the recording process
        recorder.startRecording();

        console.log("Recording started");

    }).catch(function (err) {
        //enable the record button if getUSerMedia() fails
        recordButton.disabled = false;
        stopButton.disabled = true;

    });

    //disable the record button
    recordButton.disabled = true;
    stopButton.disabled = false;
}

function stopRecording() {
    console.log("stopRecording() called");

    //stop microphone access
    gumStream.getAudioTracks()[0].stop();

    //disable the stop button
    stopButton.disabled = true;
    recordButton.disabled = false;

    //tell the recorder to finish the recording (stop recording + encode the recorded audio)
    recorder.finishRecording();

    console.log('Recording stopped');
}

function uploadRecording() {
    var formData = new FormData();

    // JavaScript file-like object
    fetch(player2.src)
        .then(res => res.blob()) // Gets the response and returns it as a blob
        .then(blob => {
            var xhr = new XMLHttpRequest();
            var fd = new FormData();
            var filename = document.getElementById('filename');
            if (filename.value === "") {
                fd.append("file", blob, "filename.wav");
            }
            else
            {
                fd.append("file", blob, filename.value + ".wav");
            }
            xhr.open("POST", "http://127.0.0.1:5000/myaudio", true);
            xhr.send(fd);
            window.location.href = "/render";
        });
}

function createDownloadLink(blob, encoding) {

    var url = URL.createObjectURL(blob);
    var au = document.createElement('audio');
    var li = document.createElement('li');
    var link = document.createElement('a');

    //add controls to the <audio> element
    au.controls = true;
    au.src = url;

    //link the a element to the blob
    link.href = url;
    link.download = new Date().toISOString() + '.' + encoding;
    link.innerHTML = link.download;

    //add the new audio and a elements to the li element
    li.appendChild(au);
    li.appendChild(link);

    //add the li element to the ordered list
    recordingsList.appendChild(li);
}


//helper function
// function __log(e, data) {
// 	log.innerHTML += "\n" + e + " " + (data || '');
// }
