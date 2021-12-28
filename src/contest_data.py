from typing import Dict, Tuple, Union

ContestName = str
TotalQuestions = Union[int, Tuple[Tuple[str, int], ...]]
YearRange = Tuple[int, int]

contests: Dict[ContestName, Tuple[TotalQuestions, YearRange]] = {
    'gauss7': (25, (2005, 2021)),
    'gauss8': (25, (2005, 2021)),
    'pascal': (25, (2005, 2021)),
    'cayley': (25, (2005, 2021)),
    'fermat': (25, (2005, 2021)),
    'fryer' : (4, (2005, 2021)),
    'galois': (4, (2005, 2021)),
    'euclid': (10, (2005, 2021)),
    'hypatia': (4, (2005, 2021)),

    'cimc': (
        (('A', 6), ('B', 3)),
        (2011, 2021)
    ),
    'csmc': (
        (('A', 6), ('B', 3)),
        (2011, 2021)
    ),
}