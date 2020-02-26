import os
import os.path
import json
import cv2

from image_boxer import ImageBBoxer

def main():
    images_path = "data/images/"
    bboxes_path = "data/bboxes/"

    if not os.path.exists(bboxes_path):
        os.makedirs(bboxes_path)

    images = os.listdir(images_path)

    for image in images:
        img = cv2.imread(images_path + image)
        boxes = ImageBBoxer().img2boxes(img)

        filename, extension = os.path.splitext(image)

        result = {
            "name": image,
            "width": img.shape[1],
            "height": img.shape[0],
            "boxes": boxes
        }

        with open(bboxes_path + filename + ".json", "w", encoding="utf-8") as file:
            json.dump(result, file, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    main()