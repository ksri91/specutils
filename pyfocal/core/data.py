from astropy.nddata import NDData, NDDataBase, NDArithmeticMixin, NDIOMixin
from .events import EventHook
import numpy as np
import logging
from astropy.units import Unit, Quantity


class Data(NDIOMixin, NDArithmeticMixin, NDData):
    """
    Class of the base data container for all data (of type
    :class:`numpy.ndarray`) that is passed around in Pyfocal. It inherits from
    :class:`astropy.nddata.NDData` and provides functionality for arithmetic
    operations, I/O, and slicing.
    """
    def __init__(self, *args, **kwargs):
        super(Data, self).__init__(*args, **kwargs)
        self._dispersion = None
        self.name = "New Data Object"
        self._layers = []

    @classmethod
    def read(cls, *args, **kwargs):
        from ..interfaces.registries import io_registry

        return io_registry.read(cls, *args, **kwargs)

    @property
    def dispersion(self):
        if self._dispersion is None:
            self._dispersion = np.arange(self.data.size)

            try:
                crval = self.wcs.wcs.crval[0]
                cdelt = self.wcs.wcs.cdelt[0]
                end = self._source.shape[0] * cdelt + crval
                self._dispersion = np.arange(crval, end, cdelt)
            except:
                logging.warning("Invalid FITS headers; constructing default "
                                "dispersion array.")

        return self._dispersion

    @property
    def dispersion_unit(self):
        try:
            return self.wcs.cunit[0]
        except AttributeError:
            logging.warning("No dispersion unit information in WCS.")

        return Unit("")


class Layer(object):
    """
    Base class to handle layers in Pyfocal.

    A layer is a "view" into a :class:`pyfocal.core.data.Data` object. It does
    not hold any data itself, but instead contains a special `mask` object
    and reference to the original data.

    Since :class:`pyfocal.core.data.Layer` inherits from
    :class:`astropy.nddata.NDDataBase` and provides the
    :class:`astropy.nddata.NDArithmeticMixin` mixin, it is also possible to
    do arithmetic operations on layers.
    """
    def __init__(self, source, mask, parent=None):
        super(Layer, self).__init__()
        self._source = source
        self._mask = mask
        self._parent = parent
        self.name = self._source.name + " Layer"
        self.layer_units = (self._source.unit, self._source.dispersion_unit)

    @property
    def data(self):
        return Quantity(self._source.data[self._mask],
                        unit=self._source.unit).to(
                self.layer_units[1])

    @property
    def dispersion(self):
        return Quantity(self._source.dispersion[self._mask],
                        unit=self._source.dispersion_unit).to(
                self.layer_units[0])

    @property
    def mask(self):
        return self._source.mask[self._mask]

    @property
    def wcs(self):
        return self._source.wcs

    @property
    def meta(self):
        return self._source.meta
