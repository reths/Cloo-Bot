
from typing import Tuple, Union

from contest_data import contests
from enum import Enum

class ContentType(Enum):
    # the user has to specify the contest type, year and question
    # optionally, they can also provide what part of the contest they want
    # if they're going for CSMC or CIMC contests
    SPECIFIC = 1
    
    # includes the part of the contest
    PSPECIFIC = 2
    
    # provide the contest type such as CSMC, CIMC, Cayley, so on
    CRANDOM = 3
    
    # will enable the computer to pick anything it wants
    RANDOM = 4

# honestly, got lazy here and didn't want to type out the entire thing
# this should be enough even though it's NOT CORRECT
Parsed = Union[Tuple[Union[str, int], ...], str]

def find_type(content: str) -> Tuple[Parsed, ContentType]:
    assert "cloo give me" in content

    if "random" in content:
        # check if it's purely random
        if content == "cloo give me random":
            return ('', ContentType.RANDOM)
        
        # we check for the type of contest that the user is looking for
        # ['', '[contest type]']
        return (
            content.split("cloo give me random ")[1], 
            ContentType.CRANDOM
        )
    
    # in this case the user has given us a more specific command
    # the string can look like the following:

    #   "cloo give me [contest type] [year] question [#] (part)"
    #   "cloo give me [contest type] [year] [#] (part)"

    splitted = (
        content
            .replace("cloo give me", "")
            .replace("question", "")
            .strip()
            .split()
    )

    assert len(splitted) >= 3, f"'{content}' is not a valid command, please ensure you've given the contest, year and question number."

    contest_type, year, num, *rest = splitted
    part = rest[0] if "part" in rest else None

    assert contest_type in contests, f"{contest_type} is not in {contests}"
    
    # allowed years
    start, end = contests[contest_type][1]
    assert start <= int(year) <= end, f"The bot only allows for the contests to be in years {start} - {end}"

    if part:
        assert contest_type in ('csmc', 'cimc'), "Only contests with parts are CSMC/CIMC"
        assert part in ('A', 'B'), "Invalid part, there are only parts A and B"
        
        assert 1 <= int(num) <= 6, "Chosen question number must be between 1 and 6"

        return (
            (contest_type, int(year), int(num), part),
            ContentType.PSPECIFIC
        )
    
    return (
        (contest_type, int(year), int(num)),
        ContentType.SPECIFIC
    )
    
