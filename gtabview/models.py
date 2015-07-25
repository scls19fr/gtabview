# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, absolute_import, generators
from .compat import *


def getitem(lst, idx, default=None):
    return lst[idx] if idx < len(lst) else default

def getitem2(lst, y, x, default=None):
    return getitem(getitem(lst, y, []), x, default)


class ExtDataModel(object):
    def shape(self):
        raise Exception()

    def header_shape(self):
        raise Exception()

    def data(self, y, x):
        raise Exception()

    def header(self, axis, x, level):
        raise Exception()

    def transpose(self):
        return TranposedExtDataModel(self)


class TranposedExtDataModel(ExtDataModel):
    def __init__(self, model):
        self._model = model

    def shape(self):
        x, y = self._model.shape()
        return (y, x)

    def header_shape(self):
        x, y = self._model.header_shape()
        return (y, x)

    def data(self, y, x):
        return self._model.data(x, y)

    def header(self, axis, x, level):
        return self._model.header(not axis, x, level)

    def transpose(self):
        return self._model



class ExtListModel(ExtDataModel):
    def __init__(self, data, hdr_rows=None, idx_cols=None):
        super(ExtListModel, self).__init__()
        if hdr_rows is None:
            hdr_rows = 1 if len(data) > 1 else 0
        if idx_cols is None:
            idx_cols = 0
        self._header_shape = (hdr_rows, idx_cols)
        self._shape = (len(data) - hdr_rows, max(map(len, data)) - idx_cols)
        self._data = data

    def shape(self):
        return self._shape

    def header_shape(self):
        return self._header_shape

    def header(self, axis, x, level):
        if axis == 0:
            return getitem2(self._data, level, x + self._header_shape[1], '')
        else:
            return getitem2(self._data, x + self._header_shape[0], level, '')

    def data(self, y, x):
        return getitem2(self._data, y + self._header_shape[0],
                        x + self._header_shape[1], '')


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
        return 1 if not hasattr(ax, 'levels') \
            else len(ax.levels)

    def shape(self):
        return self._data.shape

    def header_shape(self):
        return (self._axis_levels(0), self._axis_levels(1))

    def data(self, y, x):
        return str(self._data.iat[y, x])

    def header(self, axis, x, level=0):
        ax = self._axis(axis)
        return str(ax.values[x]) if not hasattr(ax, 'levels') \
            else str(ax.values[x][level])


def _data_lower(data):
    # TODO: add specific data models to reduce overhead
    if data.__class__.__name__ in ['Series', 'Panel']:
        return data.to_frame()
    elif isinstance(data, dict):
        return [data.keys()] + list(map(list, zip(*[data[i] for i in data.keys()])))
    return data


def as_model(data, hdr_rows=None, idx_cols=None, transpose=False):
    model = None
    if isinstance(data, ExtDataModel):
        model = data
    else:
        data = _data_lower(data)

        if hasattr(data, '__array__') and hasattr(data, 'iat') and \
           hasattr(data, 'index') and hasattr(data, 'columns'):
            model = ExtFrameModel(data)
        elif hasattr(data, '__array__') and len(data.shape) >= 2:
            model = ExtMatrixModel(data)
        elif hasattr(data, '__getitem__') and hasattr(data, '__len__') and \
             hasattr(data[0], '__getitem__') and hasattr(data[0], '__len__'):
            model = ExtListModel(data, hdr_rows=hdr_rows, idx_cols=idx_cols)
        elif hasattr(data, '__getitem__') and hasattr(data, '__len__'):
            model = ExtVectorModel(data)

    if transpose and model:
        model = model.transpose()
    return model
