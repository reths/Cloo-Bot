from typing import List, Optional, Union, Dict, Tuple

from pdf2image import convert_from_path
from re import match

import numpy as np
import cv2

def to_image(filename: str, dpi: int = 300) -> List[np.ndarray]:
    """Converts contest pdfs into images that can be manipulated with numpy"""
    
    images = [
        cv2.cvtColor( np.asarray(page), code=cv2.COLOR_RGB2BGR )
        for page in convert_from_path(
            filename,
            poppler_path="C:\\Program Files (x86)\\poppler-21.03.0\\Library\\bin", 
            dpi=dpi
        )
    ]

    # check if the first and last pages are useless and remove them if they are
    if is_unnecessary(images[0]):
        images = images[1 :]
    
    if is_unnecessary(images[-1]):
        images = images[: -1]
    
    return images

def non_empty(arr: Tuple[np.ndarray, ...]) -> bool:
    """Returns whether all the arrays are non-empty"""
    return all(ind.size != 0 for ind in arr)

def vertical_margin(image: np.ndarray) -> Optional[int]:
    """Finds the vertical margin of the image by scanning from left to right vertically."""

    offset = 0
    
    # continue while `offset` is less than image's width
    while offset < image.shape[1]:
        # check for the black pixels in a certain subset of the paper
        res = np.where(image[:, offset: offset + 50] < [50, 50, 50])

        if non_empty(res):
            xv = res[1]
            return offset + xv[0]
        
        offset += 50

def horizontal_margin(image: np.ndarray) -> Optional[int]:
    """Finds the horizontal margin of the image by scanning from bottom to top horizontally."""

    offset = 0

    # continue while `offset` is less than image length
    while offset < (y := image.shape[0]):
        # check a layer of 100 x (image length) to see if there are any black pixels
        res = np.where(
            image[y - (offset + 100): y - offset, :] < [50, 50, 50]
        )

        if non_empty(res):
            xv = res[1]

            return xv[0]
        
        offset += 100
    return None

def whitespace_markers(image: np.ndarray) -> Tuple[int, int, int]:
    """
    Given a processed image of the question, this function returns 
    the first non-black pixel from the left, right and bottom.
    """

    left = vertical_margin(image)
    right = image.shape[1] - left
    bottom = horizontal_margin(image)

    return (left, right, bottom)

def parse_data(data: Union[bytes, str]) -> Dict[int, Tuple[int, int]]:
    """
    Turns the OCR string data into dictionary of (question: position)
    Where the typical OCR string will look as such,

    level	page_num	block_num	par_num	line_num	word_num	left	top	width	height	conf	text
    1	1	0	0	0	0	0	0	396	3301	-1	
    2	1	1	0	0	0	301	503	95	2515	-1	
    3	1	1	1	0	0	301	503	95	2515	-1	
    4	1	1	1	1	0	302	503	94	31	-1	
    5	1	1	1	1	1	302	503	94	31	96.756523	Part
    4	1	1	1	2	0	304	597	27	30	-1	
    5	1	1	1	2	1	304	597	27	30	92.041115	1.
    4	1	1	1	3	0	302	787	29	30	-1	
    5	1	1	1	3	1	302	787	29	30	95.486389	2.
    4	1	1	1	4	0	302	975	29	31	-1	
    5	1	1	1	4	1	302	975	29	31	93.857849	3.
    4	1	1	1	5	0	301	1218	30	31	-1	
    5	1	1	1	5	1	301	1218	30	31	84.800049	4,
    4	1	1	1	6	0	302	1707	29	31	-1	
    5	1	1	1	6	1	302	1707	29	31	91.918594	5.
    4	1	1	1	7	0	302	2987	29	31	-1	
    5	1	1	1	7	1	302	2987	29	31	96.475555	6.
    """
    
    # each `entry` in `data` stores information about all the numbers seen
    
    # entry[-1]  = number
    # entry[-2]  = confidence
    # entry[6:8] = coordinates (x, y)
    
    storage = {}
    for entry in data.split('\n'):
        
        entry = entry.split('\t')
        found = match('\d+', entry[-1])

        if found:
            number = int(found.group(0))
            x, y = int(entry[6]), int(entry[7])
            
            if number not in storage and number <= 25:
                storage[number] = (x, y)

    if not len(storage):
        return {}

    # find the most common x position and look for outliers that aren't within 
    # some neighbourhood of that x position and remove them
    x_values = [x for (x, _) in storage.values()]
    common_x = max(set(x_values), key = x_values.count)

    return {
        question: (x, y)
        for (question, (x, y)) in storage.items()
        if common_x - 5 <= x <= common_x + 5
    }

def sanitize(img: np.ndarray, page_margin: int) -> np.ndarray:
    """Removes the block of text within rectangles at the top of papers that make it difficult to parse text."""

    bw = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    contour, _ = cv2.findContours(bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for arr in contour:
        # dismiss contour that represents the edge of the page by looking for page corner [0, 0]
        if [0, 0] in arr or len(arr.squeeze()) <= 2:
            continue

        # find all points in the neighbourhood of [margin - 5, margin + 5]
        # then find the minimum and maximum, which will be used as boundary points to crop the image
        neighbourhood = [
            (x, y) 
            for x, y in arr.squeeze()
            if (page_margin - 5 <= x <= page_margin + 5)
        ]

        if len(neighbourhood) == 2:
            (x1, y1), (_, y2) = min(neighbourhood), max(neighbourhood)

            # boundary points offset by 5 to remove lines
            img[y1 - 5: y2 + 5, x1 - 5:] = [255, 255, 255]

    return img

def is_unnecessary(image: np.ndarray) -> bool:
    """The function is a rough aproximation for whether there is an unnecessary page at the end."""

    margin = horizontal_margin(image)
    image = image[:, :margin + 50]

    return not np.array_equal(sanitize(image.copy(), margin), image)