#
# Copyright (C) 2012 - 2018 Satoru SATOH <satoru.satoh@gmail.com>
# License: MIT
#
# pylint: disable=missing-docstring,invalid-name,too-few-public-methods
# pylint: disable=ungrouped-imports
from __future__ import absolute_import

import anyconfig.backend.json.simplejson as TT

from .default import TBC, CNF_0_S, CNF_0


class HasParserTrait(TBC.HasParserTrait):

    psr = TT.Parser()
    cnf_s = CNF_0_S
    cnf = CNF_0


class Test_10(TBC.Test_10_dumps_and_loads, HasParserTrait):

    load_options = dump_options = dict(parse_int=None, indent=2)
    load_options["use_decimal"] = True
    empty_patterns = [('', {}), ('{}', {}), ('[]', []), ('null', None)]


class Test_20(TBC.Test_20_dump_and_load, HasParserTrait):
    pass

# vim:sw=4:ts=4:et:
