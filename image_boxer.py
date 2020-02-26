import pytesseract
from pytesseract import Output


class ImageBBoxer:
    def __init__(self):
        pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract'  # путь к тессеракту

    def _is_box_in(self, box1, box2):
        x1, y1, w1, h1 = box1
        x2, y2, w2, h2 = box2

        return (x1 >= x2) and (y1 >= y2) and (x1 + w1 <= x2 + w2) and (y1 + h1 <= y2 + h2)

    def _get_boxes(self, data):
        boxes = []

        for i in range(len(data['level'])):
            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]

            if (w < 5) or (h < 5) or (data['level'][i] != 4):
                continue

            boxes.append({
                'bbox': [x, y, w, h],
                'text': ''
            })

        return boxes

    def _fill_text(self, boxes, data):
        for i in range(len(data['level'])):
            if data['level'][i] != 5:
                continue

            box = data['left'][i], data['top'][i], data['width'][i], data['height'][i]

            for j in range(len(boxes)):
                if self._is_box_in(box, boxes[j]['bbox']):
                    if boxes[j]['text'] != '':
                        boxes[j]['text'] += ' '

                    boxes[j]['text'] += data['text'][i]

    def _normalize_boxes(self, boxes, width, height):
        normalized_boxes = []

        for box in boxes:
            if box['text'].isspace():
                continue

            x, y, w, h = box['bbox']

            box['bbox'] = [x / width, y / height, w / width, h / height]
            normalized_boxes.append(box)

        return normalized_boxes

    def img2boxes(self, img):
        data = pytesseract.image_to_data(img, output_type=Output.DICT, lang='eng+rus', config=r'--psm 4')
        boxes = self._get_boxes(data)

        self._fill_text(boxes, data)

        return self._normalize_boxes(boxes, img.shape[1], img.shape[0])
