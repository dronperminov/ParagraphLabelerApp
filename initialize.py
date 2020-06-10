import os
import os.path
import json
import cv2

from image_boxer import ImageBBoxer

def main():
    with open("config.json", encoding='utf-8') as f:
        config = json.load(f)

    images_dir = config["images_dir"]
    bboxes_dir = config["bboxes_dir"]

    if not os.path.exists(images_dir):
        print("images_dir '{0}' is not valid".format(images_dir))
        return

    if not os.path.exists(bboxes_dir):
        os.makedirs(bboxes_dir)

    images = os.listdir(images_dir)

    for i, image in enumerate(images):
        print("{0}/{1} ({2}): ".format(i + 1, len(images_dir + '/' + image), image), end='',)
        img = cv2.imread(images_dir + '/' + image)
        boxes = ImageBBoxer().img2boxes(img)

        filename, extension = os.path.splitext(image)

        result = {
            "name": image,
            "width": img.shape[1],
            "height": img.shape[0],
            "boxes": boxes
        }

        with open(bboxes_dir + '/' + filename + ".json", "w", encoding="utf-8") as file:
            json.dump(result, file, indent=4, ensure_ascii=False)

        print("done ({0} bboxes)".format(len(result["boxes"])))


if __name__ == '__main__':
    main()