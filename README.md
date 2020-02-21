# ParagraphLabelerApp
Implementation of адфыл application for half automatic labeling paragraphs in image of document


## Start work
* Install python3 and pip (if you haven't installed it yet)
* Install some packages via pip (`pip install -r requirements.txt`)
* Install tesseract for your OS and specify path to it:
```python
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract' # путь к тессеракту
```
* Move images for labeling to `images` folder
* Edit labels dictionary in `app.py` file for your task
```python
labels = {
	'header' : (255, 255, 0),
	'bold text' : (255, 0, 0),
	'italic text' : (255, 128, 0),
	'text' : (200, 0, 0),
	'table' : (0, 255, 0),
	'picture' : (0, 0, 255),
}
```
* Launch application using `python app.py`
* Go to `localhost:5000` and label your images

## Controls

### Get next bounding box
Press space key

### Add bounding box
While holding the left mouse button, move the cursor to another point and release the mouse button. Select the desired label in the list that appears or press the number of this label on the keyboard.

### Remove bounding box
Hover over the bounding box and click the right mouse button (for smartphones: double-click on the bounding box).

### Move bounding box
Hover over the bounding box, hold the left mouse button, move bbox to necessary point and release the mouse button.

### Resize bounding box
Hover over the border of the bounding rectangle, hold down the left mouse button, drag the border to the desired location and release the button.

### Scale image
Press `+` or `-` key to zoom in and out respectively

### Remove all bounding boxes
Press to the `reset` button.

### Save bounding boxes
Press to the `save` button and labeled image will move from `images` to the `labels` folder with creating .json file and .jpg image with bounding boxes.