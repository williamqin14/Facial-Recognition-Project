# Facial Recognition Project

# About 

An API working with facial recognition ML libraries to train and recognize custom faces on YouTube thumbnails. The program can be trained to recognize faces that can later allow for things like filtering based on thumbnail results. 

The program runs by calling the YouTube API for information, parsing the response and storing thumbnails in a list. The thumbnails are then converted into image format and immediately fed into the model for processing. After drawing boxes around identified faces and labeling them, the results are displayed in a window. 

# Installation

Project is currently not optimized for installation, but can be run by cloning the repository and running the following commands:

* cd ./face_recognizer
* python3 -m pip install -r requirements.txt

# Setup

The main module to run is detector.py. Since model has already been trained and encoded, the program can be run by simply running the following command:

* python3 detector.py

The model will run the recognize_faces command on a custom image downloaded from YouTube. It will open a window with the image and the faces detected. 

The model is also capable of running on multiple YouTube thumbnails at once, but will require a YouTube API v3 key, created in https://console.cloud.google.com/apis/api/youtube.googleapis.com. The api key is defined as API_KEY in YouTubeAPI.py.

# Version 1 Results

Version 1 of this model uses the facial_recognition library, which utilizes the dlib hog (Histogram of Oriented Gradients) model. It was trained on 10 images of each person, and was able to occassionally recognize the person with varied results (40 pages scraped from YouTube channel Dreamcatcher). Despite the limited amount of training, the results were surprisingly decent. 

* Model can recognize frontal facing facial profiles in group settings with decent accuracy. All faces were identified correctly except the right most one.

![Group kpop model](https://github.com/williamqin14/Facial-Recognition-Project/assets/84489685/a3708178-dc7a-489e-872b-8751be9bf610)

* Model can recognize isolated faces without problem.

 ![dami success](https://github.com/williamqin14/Facial-Recognition-Project/assets/84489685/87e7dd95-85c0-4b1f-b002-acfc66646d2b)

* Model has trouble with odd angle faces and small faces, which is a limitation of the hog model. The hog model was meant for frontal facing profiles with a minimum face size of 80x80 pixels.

![side profile and small face exmaple](https://github.com/williamqin14/Facial-Recognition-Project/assets/84489685/fc91166d-e346-4256-ac17-464dbb9bb558)



