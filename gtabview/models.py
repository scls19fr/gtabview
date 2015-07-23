# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, absolute_import, generators
from .compat import *


class ExtDataModel(object):
    def shape(self):
        pass

    def header_shape(self):
        pass

    def data(self, y, x):
        pass

    def header(self, axis, x, level):
        pass


class ExtListModel(ExtDataModel):
    def __init__(self, data, hdr_rows=None):
        super(ExtListModel, self).__init__()
        if hdr_rows is None:
            hdr_rows = 1 if len(data) > 1 else 0
        self._header_shape = (hdr_rows, 0)
        self._shape = (len(data) - hdr_rows, len(data[0]))
        self._data = data

    def shape(self):
        return self._shape

    def header_shape(self):
        return self._header_shape

    def header(self, axis, x, level):
        return self._data[level][x]

    def data(self, y, x):
        return self._data[y + self._header_shape[0]][x]


class ExtVectorModel(ExtDataModel):
    def __init__(self, data):
        super(ExtVectorModel, self).__init__()
        self._data = data

    def shape(self):
        return (len(self._data), 1)

    def header_shape(self):
        return (0, 0)

    def data(self, y, x):
        return self._data[y]


class ExtMatrixModel(ExtDataModel):
    def __init__(self, data):
        super(ExtMatrixModel, self).__init__()
        self._data = data

    def shape(self):
        return self._data.shape

    def header_shape(self):
        return (0, 0)

    def data(self, y, x):
        return self._data[y, x]


class ExtFrameModel(ExtDataModel):
    def __init__(self, data):
        super(ExtFrameModel, self).__init__()
        self._data = data

    def _axis(self, axis):
        return self._data.columns if axis == 0 else self._data.index

    def _axis_levels(self, axis):
        ax = self._axis(axis)
        return 1 if getattr(ax, 'levels', None) is None \
            else len(ax.levels)

    def shape(self):
        return self._data.shape

    def header_shape(self):
        return (self._axis_levels(0), self._axis_levels(1))

    def data(self, y, x):
        return str(self._data.iat[y, x])

    def header(self, axis, x, level=0):
        ax = self._axis(axis)
        return str(ax.values[x]) if getattr(ax, 'levels', None) is None \
            else str(ax.values[x][level])