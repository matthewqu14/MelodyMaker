# MelodyMaker
Final project for CS50 (Harvard University Fall 2019) accessible at https://github.com/matthewqu14/MelodyMaker. 

## Contributors
1. Kevin Huang
2. Matthew Qu
3. Patrick Song

## Description
Webapp that allows upload and recording of `.wav` audio files and converts into `.musicxml`
(the predominant sheet music file format). Webapp has registration and login functionality for users.

## Implementation

### Tech
Uses the following languages
- HTML
- CSS
- Javascript
- Python and Flask microframework

### Core Technologies
We used the following projects to help develop the web app:
- [MSnet](https://github.com/bill317996/Melody-extraction-with-melodic-segnet) used for melody extraction derived from
the paper "[A Streamlined Encoder/Decoder Architecture for Melody Extraction](https://arxiv.org/abs/1810.12947)".
- [Open Sheet Music Display](https://github.com/opensheetmusicdisplay/opensheetmusicdisplay) for rendering `.musicxml`.


### Dependencies
For webapp to work, must download [MuseScore3](https://musescore.org/en/3.0) for `.musicxml` conversion.
After installation, [create environment variable](https://www.youtube.com/watch?v=bEroNNzqlF4) `Muse` and set value to the path for MuseScore3.exe in program files
(dependent on operating system).

Project currently runs on [python 3.6.6](https://www.python.org/downloads/release/python-366/).

The project requires the following packages that can be installed using `pip3 install` for which there is a
[tutorial](https://www.youtube.com/watch?v=gFNApsyhpKk) (and more that may not be accounted for):
- pytorch (go to https://pytorch.org/ to get correct install command)
- numpy
- pysoundfile
- scipy
- math
- pypianoroll
- flask
- cs50
- subprocess
- flask-session
- flask-mail

### Running Project

Use command `flask run` in terminal to run webapp on local host.

## Project Structure

3 directories:
1. audio2midi stores the files for the audio (wav) to midi algorithm that extracts a melody from the recording uploaded.
    - input is where input files are stored
    - model is where the models are stored
    - output is where the midi and musicxml files are stored.
2. static contains static content
3. templates contains all html content

- Application file is called `app.py`.
- `helpers.py` contains helper functions.
- `users.db` is a sql database that contains user-account info and song info.

## Basic Usage

User must first register a valid account with email and password accessible through the registration tab. User will be sent a confirmation email from `melodymakerpro@gmail.com.`
Then, user will be able to access homepage. There the user will be able to record audio and then submit for transcription.
Recorded audio that is uploaded will be saved as a wav file in the inputs folder in `/audio2midi/input`.
User can then access audio files through the 'My Audio Files' tab.
After upload, user is sent to render page where only musicxml files can be selected for rendering.
Each musicxml file will be named as `*.musicxml` where * is the name was input for the audio file and is stored in `/audio2midi/output`.