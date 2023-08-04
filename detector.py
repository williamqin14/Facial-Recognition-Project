# detector.py

from pathlib import Path

import face_recognition
import pickle
from collections import Counter
from PIL import Image, ImageDraw
import requests
import numpy as np
import YouTubeAPI

DEFAULT_ENCODINGS_PATH = Path("output/encodings.pkl")

training = "training2"
Path(training).mkdir(exist_ok=True)
Path("output").mkdir(exist_ok=True)
Path("validation").mkdir(exist_ok=True)

def encode_known_faces(
    model: str = "hog", 
    encodings_location: Path = DEFAULT_ENCODINGS_PATH,
    type: str = "file",
    urls: list = [],
) -> None:
    names = []
    encodings = []

    # If face_data_type is "url", encode faces from URLs
    if (type == "url"):
        for url in urls:
            name = url
            image = url_to_image(url)

            # Detect face locations and compute face encodings
            face_locations = face_recognition.face_locations(image, model=model)
            face_encodings = face_recognition.face_encodings(image, face_locations)

            for encoding in face_encodings:
                names.append(name)
                encodings.append(encoding)
    else: # If face_data_type is "file", encode faces from local image files
        for filepath in Path(training).glob("*/*"):
            # skip uncompatible files to avoid errors
            if (not filepath.name.lower().endswith(('.png', '.jpg', '.jpeg'))): continue

            name = filepath.parent.name
            image = face_recognition.load_image_file(filepath)

            # Detect face locations and compute face encodings
            face_locations = face_recognition.face_locations(image, model=model)
            face_encodings = face_recognition.face_encodings(image, face_locations)

            for encoding in face_encodings:
                names.append(name)
                encodings.append(encoding)

    # Save the face names and encodings as a dictionary
    name_encodings = {"names": names, "encodings": encodings}
    with encodings_location.open(mode="wb") as f:
        pickle.dump(name_encodings, f)

# url = "https://i.ytimg.com/vi/bfC9GWSAQQQ/maxresdefault.jpg"

def url_to_image(url):
    image = Image.open(requests.get(url, stream=True).raw).convert('RGB')
    return np.array(image)

# encode_known_faces(type="url", urls=["https://i.ytimg.com/vi/bfC9GWSAQQQ/maxresdefault.jpg"])


BOUNDING_BOX_COLOR = "blue"
TEXT_COLOR = "white"

def _display_face(draw, bounding_box, name):
    top, right, bottom, left = bounding_box
    draw.rectangle(((left, top), (right, bottom)), outline=BOUNDING_BOX_COLOR)
    text_left, text_top, text_right, text_bottom = draw.textbbox(
        (left, bottom), name
    )
    draw.rectangle(
        ((text_left, text_top), (text_right, text_bottom)),
        fill="blue",
        outline="blue",
    )
    draw.text(
        (text_left, text_top),
        name,
        fill="white",
    )

def _recognize_face(unknown_encoding, loaded_encodings):
    boolean_matches = face_recognition.compare_faces(
        loaded_encodings["encodings"], unknown_encoding
    )
    votes = Counter(
        name
        for match, name in zip(boolean_matches, loaded_encodings["names"])
        if match
    )
    if votes:
        return votes.most_common(1)[0][0]

def recognize_faces(
    image_location: str,
    model: str = "hog",
    encodings_location: Path = DEFAULT_ENCODINGS_PATH,
    type: str = "file",
) -> None:
    with encodings_location.open(mode="rb") as f:
        loaded_encodings = pickle.load(f)
    
    if (type == "url"):
        input_image = url_to_image(image_location)
    else:
        input_image = face_recognition.load_image_file(image_location)

    input_face_locations = face_recognition.face_locations(
        input_image, model=model
    )
    input_face_encodings = face_recognition.face_encodings(
        input_image, input_face_locations
    )

    pillow_image = Image.fromarray(input_image)
    draw = ImageDraw.Draw(pillow_image)

    for bounding_box, unknown_encoding in zip(
    input_face_locations, input_face_encodings
    ):
        name = _recognize_face(unknown_encoding, loaded_encodings)
        if not name:
            name = "Unknown"
        # print(name, bounding_box)
        _display_face(draw, bounding_box, name)

    del draw
    pillow_image.show()
    
def validate(model: str = "hog", type: str = "file", urls: list = []):
    if (type == "url"):
        for url in urls:
            recognize_faces(
                image_location=url, model=model, type="url"
            )
    else:
        for filepath in Path("validation").rglob("*"):
            if filepath.is_file():
                recognize_faces(
                    image_location=str(filepath.absolute()), model=model
                )

# recognize_faces("Actor-Ben-Affleck-premiere-AIR-March-2023.jpeg")
recognize_faces("https://i.ytimg.com/vi/bfC9GWSAQQQ/maxresdefault.jpg", type="url")
# encode_known_faces()
# response_urls = YouTubeAPI.get_video_thumbnail_urls("https://www.youtube.com/watch?v=bfC9GWSAQQQ")
# validate(type="url", urls=response_urls)

# validate(type="url", urls=YouTubeAPI.get_video_thumbnail_urls("https://www.youtube.com/channel/UCijULR2sXLutCRBtW3_WEfA", 3))