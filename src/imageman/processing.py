from urllib.request import urlretrieve

from .exceptions import *
from .utility import *

import pytesseract as pyt

def get_question(pdf: str, question: int, part: Optional[str] = '') -> np.ndarray:
    """given a pdf file of the contest, and the question, a picture of the question will be returned"""

    images = to_image(pdf)
    p_margin = vertical_margin(images[0])

    margin = min(
        hor_img_margin 
        for image in images 
        
        # filter to remove any undefined margin
        if (hor_img_margin := horizontal_margin(image))
    ) - 10
    
    width = images[0].shape[1]

    # sometimes the horizontal margin is incorrect in cases where there are shapes at the bottom of the page
    # that might end up causing the margin to be way off to the side, a way to prevent that is to bound the margin
    if margin > width / 4:
        margin = p_margin + 50

    # path = C:\Program Files\Tesseract-OCR
    pyt.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract"

    # there can be multiple questions of the same number in different part
    # this will store all of them
    variants = []

    for page_no, image in enumerate(images):
        
        # crop up to the margin horizontally and copy
        cropped = image[:, :margin + 20].copy()
        sanitized = sanitize(cropped, p_margin)

        # collect all the data
        data = pyt.image_to_data(sanitized, config='--psm 6 --oem 3 tessedit_char_whitelist=123456789')

        # parsed version of `data` which only has the information that we need 
        information = parse_data(data)
        
        if question not in information:
            continue

        py, px = image.shape[: -1]
        _, y1 = information[question]

        # this part detects the next question and grabs its y coordinate so there is another point to crop from
        keys = list(information.keys())

        if question + 1 in information:
            _, y2 = information[question + 1]
  
        # some papers are partitioned and because of that there is a sudden switch in the question number pattern
        # for example, in CSMC2021, the `information` dict for 2nd page would look as follow: {5: ..., 6: ..., 1: ...} instead of, {5: ..., 6: ..., 7: ...}
        # in these instances we have to check whether `keys[keys.index(question) + 1]` exists
        elif keys.index(question) + 1 < len(keys):
            next_key = keys[keys.index(question) + 1]
            _, y2 = information[next_key]

        else:
            # if neither of the two work, use the end of the page as the cropping point
            y2 = py
        
        variants.append((page_no, y1, y2))

    # responsible for finding out which variant to use depending on which `part` specified
    # if no `part` is specified then the first variant of the question is selected
    mapping = {'A': 0, 'B': 1, 'C': 2}
    
    contest_name = pdf.replace('.pdf', '')
    if part and part not in mapping:
        raise InvalidPart(contest_name, part)

    if variants:
        page_no, y1, y2 = variants[mapping[part]] if part else variants[0]
        image = images[page_no][y1 - 50: y2 - 50, :px]

        # automatically crops the image depending on where the whitespace ends
        left, right, _ = whitespace_markers(image)

        return image[:, left - 50: right]
    else:
        
        # `question` and `part` will be used to give message to server
        raise QuestionNotDetected(contest_name, question, part)

def save_image(img: np.ndarray):
    cv2.imwrite('saved.jpeg', img)

def save_contest(name: str, year: Union[int, str]) -> str:
    """finds waterloo contest paper then saves locally as pdf, and returns name"""

    # general link for non-CIMC/CSMC papers:
    # https://www.cemc.uwaterloo.ca/contests/past_contests/{year}/{year}{name}Contest.pdf
    # where `year` is a valid year in which the contest was done, and `name` is a capitalized str

    # general link for CIMC/CSMC papers:
    # https://www.cemc.uwaterloo.ca/contests/past_contests/{year}/{year}{name}.pdf
    # here, `name` represents the abbreviated forms: CIMC and CSMC

    name = name.lower()
    inner_name = name.upper() if name in ['csmc', 'cimc'] else name.capitalize() + 'Contest'

    urlretrieve(
        f'https://www.cemc.uwaterloo.ca/contests/past_contests/{year}/{year}{inner_name}.pdf', 
        filename := f'{name}.pdf'
    )

    return filename