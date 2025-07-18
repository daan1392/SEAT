from SEAT.nuclides import nuclide2element
import SEAT.natural
import numpy as np
import SEAT._names
import pkg_resources

__author__ = "Federico Grimaldi"
__all__ = [
    "are_elements",
    "are_nuclides",
    "unfold_composite",
    "get_existing_xs",
    "pollute",
    "enrich",
]

XSDATA_FOLDER = pkg_resources.resource_filename(SEAT._names.PAKAGE_NAME,
                                                f'{SEAT._names.XSDATA_FOLDER_NAME}/')

def are_elements(keys: set[str]) -> bool:
    """
    Checks whether all the items of a set are element symbols.

    Parameters
    ----------
    keys : set[str]
        the set of strings to check.

    Returns
    -------
    bool
        True if all the items in the `keys` are element symbols.

    """
    return bool(np.prod(([k.isalpha() for k in keys])))

def are_nuclides(keys: set[str]) -> bool:
    """
    Checks whether all the items of a set are nuclide symbols.

    Parameters
    ----------
    keys : set[str]
        the set of strings to check.

    Returns
    -------
    bool
        True if all the items in the `keys` are nuclide symbols.

    Note
    ----
    Does not check the existence of a nuclide. It rather checks the format.

    """
    return bool(np.prod([k.isalnum() for k in keys])) and bool(np.prod([not k.isalpha() for k in keys]))

def unfold_composite(composite: dict[str, float]) -> dict[str, float]:
    """
    Unfrolds a number of elements to teir isotopic compositions

    Parameters
    ----------
    composite : dict[str, float]
        * key: the element symbols.
        * float: the corresponding abundances.

    Returns
    -------
    dict[str, float]
        * key: the nuclide symbols.
        * values: the corresponding abundances.

    """
    return {k: v * share
            for element, share in composite.items()
            for k, v in getattr(SEAT.natural, element).items()}

def unfold_element_input(composite: str, floating_points: int = 9) -> dict[str, float]:
    """
    Unfolds a string taken from the input file to a dictionary 
    and also prints the result so it can be copied to the input file.
    
    Parameters
    ----------
    composite : str
        A string containing the element symbol and its abundance, e.g.:
        '6000.03c 1.00'.
        
    Returns
    -------
    dict[str, float]
        A dictionary with element symbols as keys and their abundances as values.
        
    Examples
    --------
    >>> unfold_element_input("6000.03c      1")
    # Printed:
    # 6012.03c    0.989300000
    # 6013.03c    0.010700000
    # Returned:
    {'C12': 0.9893, 'C13': 0.0107}
    """
    za_id, abundance = composite.split()[:2]
    za = int(za_id.split(".")[0])
    identifier = za_id.split(".")[1]

    unfolded = unfold_composite({SEAT.nuclides.za2element(za): float(abundance)})

    for key, item in unfolded.items():
        print(f"{SEAT.nuclides.nuclide2za(key)[0]}.{identifier}    {item:.9f}")

    return unfolded

def get_existing_xs(library: str) -> set:
    """
    Retrieves a set of nuclides which cross sections is evaluated in the given
    library.
    Takes the data from the files stored in the `xsdata` folder.

    Parameters
    ----------
    library : str
        the library of which the available cross section set should be got.
        Available `library` values are:
            - 'endfb71': ENDF/B-VII.1
            - 'endfb80': ENDF/B-VII.1
            - 'jeff32': JEFF-3.2
            - 'jeff33': JEFF-3.3
            - 'jeff40t1': JEFF-4.0 test version 1
            - 'jeff312': JEFF-3.1.2
            - 'jendl40u': JENDL-4.0u

    Returns
    -------
    set
        nuclide symbols `'Nnxxx'` of which the cross section is evaluated
        in `library`.

    """
    XSDATA_FILE = pkg_resources.resource_filename(SEAT._names.PAKAGE_NAME,
                                                  f'{SEAT._names.XSDATA_FOLDER_NAME}/{library}.{SEAT._names.XSDATA_FILE_EXTENSION}')
    with open(XSDATA_FILE) as f:
        read = {line.strip() for line in f.readlines()}
    return read

def pollute(abundance: dict[str, float], pollutants: dict[str, float]) -> dict[str, float]:
    """
    Pollutes one nuclide-defined material with some exetrnal nuclides.

    Parameters
    ----------
    abundance : dict[str: float]
        * key: the symbol of the nuclide in the reference material
        * value: the fraction of the nuclide in the reference material.
    pollutants : dict[str: float]
        * key: the symbol of the of the pollutant nuclide
        * value: the pollution fraction (>0, <1).

    Returns
    -------
    dict[str, float]
        * key: the symbol of the nuclide
        * value: the modified atomic density.

    """
    polluted = pollutants.copy()
    for nuclide, share in abundance.items():
        polluted[nuclide] = abundance[nuclide] -\
                            abundance[nuclide] * sum(pollutants.values())
    return polluted

def enrich(abundance: dict[str: float], enrichers: dict[str, float]) -> dict[str, float]:
    """
    Enriches one nuclide-defined material in a set of nuclides.

    Parameters
    ----------
    abundance : dict[str: float]
        * key: the nuclide symbol in the reference material
        * value: the fraction of the nuclide in the reference material.
    enrichers : dict[str, float]
        * key: the symbol of the isotope to enrich (should all be isotopes of
                the same element)
        * value: the enrichment fraction (>=0, <1).

    Returns
    -------
    dict
        * key: the symbol of the nuclide
        * value: the modified atomic density.

    """
    enriched = {}
    enriched_element = nuclide2element(list(enrichers.keys())[0])
    for nuclide, share in abundance.items():
        if nuclide in enrichers.keys():
            enriched[nuclide] = enrichers[nuclide]
        elif nuclide2element(nuclide) != enriched_element:
            enriched[nuclide] = abundance[nuclide]
        else:
            enriched[nuclide] = abundance[nuclide] -\
                                sum([v - abundance[k] for k, v in enrichers.items()]) * share /\
                                sum([v for k, v in abundance.items()
                                                if nuclide2element(k) == enriched_element
                                                and k not in enrichers.keys()])
    return enriched
