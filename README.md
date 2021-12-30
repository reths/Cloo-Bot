# Cloo-Bot
Cloo-Bot provides you with a fast and efficient way to view specific or randomized Waterloo Math Contest questions that you can use to practice with your friends or yourself.

![Completely random contest question](https://media.giphy.com/media/SeP4qW7av1zNndKL0B/giphy.gif)
![Random question from a specific contest](https://media.giphy.com/media/csUD29rKvYCoqB62aQ/giphy.gif)
![Specific question from a contest](https://media.giphy.com/media/u8Q4KYlnntddFNSZ9N/giphy.gif)

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

## Problems
