# Cloo-Bot
Cloo-Bot provides you with a fast and efficient way to view specific or randomized Waterloo Math Contest questions that you can use to practice with your friends or yourself.

![Completely random contest question](https://user-images.githubusercontent.com/89747038/147791158-f003031e-dcad-4104-ba5c-7f0bd3a80af0.gif)
![Random question from a specific contest](https://user-images.githubusercontent.com/89747038/147791170-d2a15832-067f-4452-adad-e283d68b9375.gif)
![Specific question from a contest](https://user-images.githubusercontent.com/89747038/147791127-772ff013-d9ec-412c-9743-0aba143b552c.gif)

## Setup

Use `pip install pdf2image, pytesseract, opencv-python` to install the three necessary packages.

1. `pdf2image >= 1.16.0`

You must also manually install [`poppler`](https://github.com/Belval/pdf2image#windows) and include the path in [src/imageman/utility](https://github.com/reths/Cloo-Bot/blob/main/src/imageman/utility.py#L16).

2. `pytesseract >= 0.3.8`

After installation, include the path in [src/imageman/processing](https://github.com/reths/Cloo-Bot/blob/main/src/imageman/processing.py#L30).

## Usage

In each command, you will be given information about which contest and year the question is from.

`cloo give me random` gives you a random question from a random contest.

`cloo give me random [contest name]` gives you a random question from the contest specified.

`cloo give me [contest name] [year] (question) [question number]` gives you the exact question from the contest specified.

**Note**: `(question)` indicates that "question" is optional.

## Implementation Details

1. User command is parsed through the [`find_type`](https://github.com/reths/Cloo-Bot/blob/main/src/mparser.py#L26) function which checks for the validity of the command and returns command type. This information is then used in the [`on_message`](https://github.com/reths/Cloo-Bot/blob/main/src/main.py#L23) function in `src/main` to download the PDF of the contest with [`save_contest`](https://github.com/reths/Cloo-Bot/blob/main/src/imageman/processing.py#L97).

2. The main algorithm requires information about page margins which cannot be found through PDFs, however, it is possible to approximate where the margins may be through heuristics if it were an image instead. So the [`to_image`](https://github.com/reths/Cloo-Bot/blob/54cd8f98b267b5902c349c070d92d31153ceb237/src/imageman/utility.py#L9) function is used to convert the PDF pages into images. Unnecessary pages such as the first and last are removed in the case their margins may heavily disrupt the average margin size. The [`is_unnecessary`](https://github.com/reths/Cloo-Bot/blob/54cd8f98b267b5902c349c070d92d31153ceb237/src/imageman/utility.py#L167) function is responsible for this and uses heuristics to determine if the pages should be removed.

3. In the scenario of a simple contest PDF (each contest has varying formats and that is one of the problems that will be discussed) such as the [2021 Pascal Contest](https://www.cemc.uwaterloo.ca/contests/past_contests/2021/2021PascalContest.pdf) the `horizontal_margin` and `vertial_margin` functions will be used to find the best left-margin that could be used throughout all the pages. The location is then used to crop the page as shown in the illustration:

![Horizontal and Vertical Margin used to crop the page](https://user-images.githubusercontent.com/89747038/147799501-e977e17d-2101-4654-bce7-ba93071d1a48.png)

OCR is used on the cropped image at the right to see where the questions are, however `pytesseract`'s OCR will not work on this due to the lines present in the box. So to remove that, the [`sanitize`](https://github.com/reths/Cloo-Bot/blob/main/src/imageman/utility.py#L140) function is [used](https://github.com/reths/Cloo-Bot/blob/main/src/imageman/processing.py#L40) which will remove any such boxes through contour detection in opencv. After which the cropped image will look similar to the following:

![Sanitized version of the cropped image](https://user-images.githubusercontent.com/89747038/147800397-7cdba512-8972-4ecd-8d33-a195dae9a6fc.png)

4. `pytesseract` gives a string result, which is parsed through [`parse_data`](https://github.com/reths/Cloo-Bot/blob/main/src/imageman/utility.py#L82). Finally, the parsed result is used to find the location of the question (and the [next question](https://github.com/reths/Cloo-Bot/blob/main/src/imageman/processing.py#L57)), through which the wanted question is [cropped](https://github.com/reths/Cloo-Bot/blob/main/src/imageman/processing.py#L82) and sent to the user on discord.

## Problems

...
