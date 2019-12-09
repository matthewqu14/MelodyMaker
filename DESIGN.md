# MelodyMaker
Final Project for CS50

## Contributors
1. Kevin Huang
2. Matthew Qu
3. Patrick Song

#Design

For our project, we first wanted to create a database that stores
user information. For this purpose, we imported the 
login and registration functionality from the 
Finance problem set of the Web track. However, we also added
additional functionality to add complexity to the database.
In addition to the existing columns on our users table in
the SQL database, we also added a "confirmed" column in the 
database

   The purpose of the "confirmed" column is to 
officially register users only after they have clicked on 
a confirmation email link in their inbox. After registering 
on the website, users will be sent an email that is sent 
through the mail.send() function in flask-mail. Using the s.loads()
function in flask-mail, we implemented a feature that makes
the confirmation link time-senstive: after twenty minutes, the
confirmation link will expire due to securtity purposes. After
the user clicks on the confirmation link, the "confirmed" column
in the databse will be changed from the default value of "false
" to "true", giving the user full access to the website.

In addition to adding a registration confirmation feature to our
project, we also created another database called "audio". This
database stores the file names of the recordings that individuals
upload and the date in which these recordings were uploaded to
the website. This allows users to view past recordings from 
previous projects.

The back-end design was mainly motivated by the goal to convert
an audio file to a file that supported the display of sheet 
music. Automatic Music Transcription (AMT) is currently an active
field of research for machine learning. As such, finding a good
algorithm that was publicly available on github and that was easy
to use was a struggle. We eventually landed on
https://github.com/bill317996/Audio-to-midi which is an application
that is able to extract a melody from an audio file and convert it
into a midi file. It is based off the paper titled "[A Streamlined
Encoder/Decoder Architecture for Melody
Extraction](https://arxiv.org/abs/1810.12947)". The algorithm is
naturally not yet 100% accurate as the research of the subject has
not yet achieved that technical capability.

For the transcription of midi to musicxml, there were not any
publically available, free apis that we could identify so we instead
used the musescore functionality to convert the midi file to a
musicxml file. However, that necessitated that the user install
musescore3 which we thought was a tradeoff that we were willing
to sacrifice.

The music algorithm that we implemented takes a .wav file as the
input and creates a .xml file as the output file. We initially
wanted the webpage to automatically generate the sheet music
after uploading. However, because most browsers do not allow
local files to be opened automatically due to security reasons, 
we could not implement this feature. Instead, we had an input
element on our HTML page so that the user gives access to 
our website. We also wanted to implement a feature that could
directly transcribe sheet music from the table that contains
all of the recordings that the user uploaded. However, we 
encountered the same issue where the web browser denied the 
program permission to directly access files on a user's 
computer.

In order to make our website look more professional, we added
some additional design elements to our HTML and CSS files. On
the homepage, we added a paralax scrolling feature that gave
a "scrolling" animation as the user explored our homepage.
This was implemented by creating a paralax "div class" in
our HTML and specifying certain restrictions in the CSS
file that could create the scrolling effect. 