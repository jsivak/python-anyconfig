#
# Copyright (C) 2018 - 2021 Satoru SATOH <satoru.satoh @ gmail.com>
# SPDX-License-Identifier: MIT
#
r"""Common functions and variables.
"""
import typing

from ..models import processor


ProcT = typing.TypeVar('ProcT', bound=processor.Processor)
ProcClsT = typing.Type[ProcT]
ProcClssT = typing.List[ProcClsT]

# vim:sw=4:ts=4:et:
