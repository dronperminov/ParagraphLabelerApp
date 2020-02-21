import os
import random
import json
import cv2

import pytesseract
from pytesseract import Output

from flask import Flask
from flask import request, send_file, redirect, send_from_directory

pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract' # путь к тессеракту

app = Flask(__name__)
	
app.config['IMAGES_FOLDER'] = 'images' # папка с изображениями для разметки
app.config['LABELS_FOLDER'] = 'labeled' # папка для сохраняемых изображений и разметок
app.config['JS_FOLDER'] = 'js' # папка с js кодом
app.config['CSS_FOLDER'] = 'css' # папка со стилями

# метки и соответствующие им цвета (BGR формат)
labels = {
	'header' : (255, 0, 0),
	'bold text' : (255, 0, 0),
	'italic text' : (255, 0, 0),
	'text' : (255, 0, 0),
	'table' : (0, 255, 0),
	'picture' : (0, 0, 255),
}

@app.route('/images/<filename>')
def image_file(filename):
	return send_from_directory(app.config['IMAGES_FOLDER'], filename)

@app.route('/js/<filename>')
def js_file(filename):
	return send_from_directory(app.config['JS_FOLDER'], filename)

@app.route('/css/<filename>')
def css_file(filename):
	return send_from_directory(app.config['CSS_FOLDER'], filename)

def get_js_colors():
	return str([str(r) + ', ' + str(g) + ', ' + str(b) for b, g, r in labels.values()])

def get_labels_info():
	info = [str(i + 1) + ' - ' + label for i, label in enumerate(labels.keys())]
	return "0 - skip, " + str(info)[1:-1].replace("'", "")

def is_box_in(box1, box2):
	x1, y1, w1, h1 = box1
	x2, y2, w2, h2 = box2

	return (x1 >= x2) and (y1 >= y2) and (x1 + w1 <= x2 + w2) and (y1 + h1 <= y2 + h2)

def img2boxes(img):
	d = pytesseract.image_to_data(img, output_type=Output.DICT, lang='eng+rus')
	boxes = []

	height = img.shape[0]
	width = img.shape[1]

	for i in range(len(d['level'])):
		x, y, w, h = d['left'][i], d['top'][i], d['width'][i], d['height'][i]

		if (w < 5) or (h < 5):
			continue
			
		box = dict()
		box['bbox'] = [ x / width, y / height, w / width, h / height ]
		box['text'] = ''

		if d['level'][i] == 4:
			boxes.append(box)

	return boxes

def make_labeler(filename, total, boxes, iw, ih):
	initialize = "const init_boxes = ["

	for box in boxes:
		label = 'text'
		x, y, w, h = box['bbox']

		initialize += "{ label: '" + label + "', x: " + str(x) + ", y: " + str(y) + ", width: " + str(w) + ", height: " + str(h) + " },\n"

	initialize += "]\n"

	return '''
		<!DOCTYPE html>
		<html>
		<head>
			<title>Средство для разметки изображений</title>
			<meta charset="utf-8">
			<meta name="viewport" content="width=device-width,initial-scale=1.0,user-scalable=no" />
			<link rel="stylesheet" href="css/labeler.css" />
		</head>
		<body>
			<h1>Bounding box annotator (осталось разметить: {total})</h1>

			<div class="labeler" draggable=false oncontextmenu="return false;">
				<input id="mode-box" type="checkbox"/>
				<div class="labeler-image" draggable=false>
					<img id="img" src="/images/{filename}" draggable=false">
				</div>

				<div class="labeler-menu">
					<div class="labeler-entities">
						<textarea id="entities-data" cols=10 readonly></textarea>
					</div>

					<div class="labeler-tools">
						<input class="btn" type="submit" id="reset-btn" value="reset"></input>
						<input class="btn" type="submit" id="skip-btn" value="skip"></input>
						<input class="btn" type="submit" id="save-btn" value="save"></input>
					</div>

					<div class="labeler-instruction">
						<p><b>Удалить выделение</b>: правая кнопка мыши</p>
						<p><b>Получить очередной bbox</b>: пробел</p>
						<p><b>Клавиши выделения</b>: {info}</p>
					</div>
				</div>
			</div>

			<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
			<script src="js/labeler.js"></script>

			<script type="text/javascript">
				const IMAGE_WIDTH = {iw}
				const IMAGE_HEIGHT = {ih}
				const labels = {labels}
				const colors = {colors}

			   	{initialize}

				var labeler = new Labeler(labels, colors, init_boxes)			   	

				$("#save-btn").click(function(e) {{
					if (confirm("Saving: are you sure?")) {{
						window.location.replace('/save?entities=' + $("#entities-data").text())
					}}
				}})

				$("#skip-btn").click(function(e) {{
					window.location.replace('/')
				}})
			</script>
		</body>
		</html>
			'''.format(filename=filename, total=total, labels=str(list(labels.keys())), colors=get_js_colors(), info=get_labels_info(), initialize=initialize, ih=ih, iw=iw)

@app.route('/', methods=['GET'])
def label_image():
	images = os.listdir(app.config['IMAGES_FOLDER']) # получаем все доступные изображения

	if len(images) == 0: # если их нет, то и размечать нечего
		return "Все изображения были размечены"

	image = random.choice(images)
	img = cv2.imread(app.config['IMAGES_FOLDER'] + '/' + image)
	boxes = img2boxes(img)

	return make_labeler(image, len(images), boxes, img.shape[1], img.shape[0]) # иначе создаём страницу с интерфейсом для разметки

# сохранение изображения с отрисовкой разметки
def draw_labeling(name, data):
	img = cv2.imread(app.config['IMAGES_FOLDER'] + '/' + name) # открываем размеченное изображение

	for entity in data['entities']:
		label = entity['label']
		x1 = int(entity['x'])
		y1 = int(entity['y'])
		x2 = int((entity['x'] + entity['width']))
		y2 = int((entity['y'] + entity['height']))

		color = labels[label] # получаем цвет метки

		# накладываем слегка прозрачный bbox с выделенным объектом на картинку
		tmp = img.copy()
		cv2.rectangle(tmp, (x1, y1), (x2, y2), color, -1)
		cv2.addWeighted(img, 0.8, tmp, 0.2, 0, img)
		cv2.putText(img, label, (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)
		cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

	cv2.imwrite(app.config['LABELS_FOLDER'] + '/test_' + name, img) # сохраняем созданное изображение

@app.route('/save')
def save_file():
	data = json.loads(request.args.get('entities')) # получаем размеченные объекты из json
	name = data['name'] # получаем имя изображения

	draw_labeling(name.strip("/"), data) # отрисовываем результат разметки
	
	os.replace(app.config['IMAGES_FOLDER'] + '/' + name, app.config['LABELS_FOLDER'] + '/' + name) # перемещаем изображение в папку размеченных изображений

	with open(app.config['LABELS_FOLDER'] + '/' + name + '.json', 'w') as outfile:
		json.dump(data, outfile, indent=4) # сохраняем json с объектами

	return redirect("/") # возвращаем на страницу разметки

if __name__ == '__main__':
	if not os.path.exists(app.config['LABELS_FOLDER']): # если папка с размеченными изображениями ещё не создана
		os.makedirs(app.config['LABELS_FOLDER']) # создаём её

	app.run(debug=True)