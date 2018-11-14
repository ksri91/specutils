import logging
import six
import os
from ...spectra import Spectrum1D
from ..registers import data_loader
from astropy.table import Table
from ..parsing_utils import (generic_spectrum_from_table,
                             spectrum_from_column_mapping)


def identify_ecsv(origin, *args, **kwargs):
    """Check if it's an ECSV file."""
    return (isinstance(args[0], six.string_types) and
            os.path.splitext(args[0].lower())[1] == '.ecsv')


@data_loader("ECSV", identifier=identify_ecsv, dtype=Spectrum1D)
def generic_ecsv(file_name, column_mapping=None, **kwargs):
    """
    Read a spectrum from an ECSV file, using generic_spectrum_from_table_loader()
    to try to figure out which column is which.

    Parameters
    ----------
    file_name: str
        The path to the ECSV file.
    column_mapping : dict
        A dictionary describing the relation between the ECSV file columns
        and the arguments of the `Spectrum1D` class, along with unit
        information. The dictionary keys should be the ECSV file column names
        while the values should be a two-tuple where the first element is the
        associated `Spectrum1D` keyword argument, and the second element is the
        unit for the ECSV file column::

            column_mapping = {'FLUX': ('flux': 'Jy')}

    Returns
    -------
    data: Spectrum1D
        The spectrum that is represented by the data in this table.
    """
    table = Table.read(file_name, format='ascii.ecsv')

    if column_mapping is None:
        return generic_spectrum_from_table(table, **kwargs)

    return spectrum_from_column_mapping(table, column_mapping)
