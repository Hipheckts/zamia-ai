#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#
# Copyright 2015, 2016, 2017 Guenter Bartsch
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
# HAL-PROLOG compiler
#

import os
import sys
import logging
import codecs
import re

from optparse import OptionParser
from StringIO import StringIO
from copy import copy

from sqlalchemy.orm import sessionmaker

import model
from logic import *
from logicdb import *
from prolog_parser import PrologParser, SYM_EOF, PrologError
from prolog_ai_engine import PrologAIEngine
import utils

from speech_tokenizer import tokenize

class PrologCompiler(object):

    def __init__(self, session, trace = False, run_tests = False):

        self.session   = session
        self.trace     = trace
        self.run_tests = run_tests

    def set_trace (self, trace):
        self.trace = trace

    def set_run_tests (self, run_tests):
        self.run_tests = run_tests

    def nlp_macro(self, clause):

        args = clause.head.args

        name = args[0].s

        mappings = []

        for m in args[1:]:

            if m.name != 'map':
                raise Exception ('map structure expected in nlp_macro %s' % name)

            mapping = {}

            for p in m.args:
                mapping[p.name] = p.args[0].s

            mappings.append(mapping)

        # print repr(mappings)

        self.nlp_macros[name] = mappings

        
    def nlp_gen(self, module_name, clause):

        args = clause.head.args

        lang = args[0].name

        # extract all macros used

        macro_names = set()

        argc = 1
        while argc < len(args):

            nlp   = args[argc  ].s
            preds = args[argc+1].s

            argc += 2

            for pos, char in enumerate(nlp):

                if char == '@':

                    macro = re.match(r'@([A-Z]+):', nlp[pos:])

                    # print "MACRO:", macro.group(1)

                    macro_names.add(macro.group(1))

        # generate all macro-expansions

        macro_names = sorted(macro_names)
        todo = [ (0, {}) ]

        while True:

            if len(todo) == 0:
                break

            idx, mappings = todo.pop(0)

            if idx < len(macro_names):

                macro_name = macro_names[idx]

                for v in self.nlp_macros[macro_name]:

                    nm = copy(mappings)
                    # nm[macro_name] = (v, self.nlp_macros[macro_name][v])
                    nm[macro_name] = v

                    todo.append ( (idx+1, nm) )

            else:

                # generate discourse for this set of mappings

                # print repr(mappings)

                # create discourse in db

                discourse = model.Discourse(num_participants = 2,
                                            lang             = lang,
                                            module           = module_name)
                self.session.add(discourse)

                argc       = 1
                round_num = 0
                while argc < len(args):

                    s = args[argc  ].s
                    p = args[argc+1].s

                    argc += 2

                    for k in mappings:

                        for v in mappings[k]:

                            s = s.replace('@'+k+':'+v, mappings[k][v])
                            p = p.replace('@'+k+':'+v, mappings[k][v])

                    inp_raw = utils.compress_ws(s.lstrip().rstrip())
                    p       = utils.compress_ws(p.lstrip().rstrip())

                    # print s
                    # print p

                    # tokenize strings, wrap them into say() calls

                    inp_tokenized = ' '.join(tokenize(inp_raw, lang))

                    preds = p.split(';')
                    np = ''
                    for pr in preds:
                        if not pr.startswith('"'):
                            if len(np)>0:
                                np += ';'
                            np += pr.strip()
                            continue

                        for word in tokenize (pr, lang):
                            if len(np)>0:
                                np += ';'
                            np += 'say(' + lang + ', "' + word + '")'

                        if len(p) > 2:
                            if p[len(p)-2] in ['.', '?', '!']:
                                if len(np)>0:
                                    np += ';'
                                np += 'say(' + lang + ', "' + p[len(p)-2] + '")'
                        np += ';eou'


                    dr = model.DiscourseRound(inp_raw       = inp_raw, 
                                              inp_tokenized = inp_tokenized,
                                              response      = np, 
                                              discourse     = discourse, 
                                              round_num     = round_num)
                    self.session.add(dr)

                    round_num += 1

    def nlp_test(self, clause):

        args = clause.head.args

        lang = args[0].name

        # extract test rounds, look up matching discourses

        rounds        = [] # [ (in, out, actions), ...]
        round_num     = 0
        discourse_ids = set()

        for ivr in args[1:]:

            if ivr.name != 'ivr':
                raise PrologError ('nlp_test: ivr predicate args expected.')

            test_in = ''
            test_out = ''
            test_actions = []

            for e in ivr.args:

                if e.name == 'in':
                    test_in = ' '.join(tokenize(e.args[0].s, lang))
                elif e.name == 'out':
                    test_out = ' '.join(tokenize(e.args[0].s, lang))
                elif e.name == 'action':
                    test_actions.append(e.args)
                else:
                    raise PrologError (u'nlp_test: ivr predicate: unexpected arg: ' + unicode(e))
               
            rounds.append((test_in, test_out, test_actions))

            # look up matching discourse_ids:

            d_ids = set()
            
            for dr in self.session.query(model.DiscourseRound).filter(model.DiscourseRound.inp_tokenized==test_in) \
                                                              .filter(model.DiscourseRound.round_num==round_num).all():
                d_ids.add(dr.discourse_id)

            if round_num==0:
                discourse_ids = d_ids
            else:
                discourse_ids = discourse_ids & d_ids

            # print 'discourse_ids:', repr(discourse_ids)

            round_num += 1

        if len(discourse_ids) == 0:
            raise PrologError ('nlp_test: %s: no matching discourse found.' % clause.location)

        nlp_test_parser = PrologParser()

        # run the test(s): look up reaction to input in db, execute it, check result
        for did in discourse_ids:
            self.nlp_test_engine.reset_context()

            round_num = 0
            for dr in self.session.query(model.DiscourseRound).filter(model.DiscourseRound.discourse_id==did) \
                                                              .order_by(model.DiscourseRound.round_num):
            
                prolog_s = ','.join(dr.response.split(';'))

                logging.info("nlp_test: %s round=%3d, %s => %s" % (clause.location, round_num, dr.inp_tokenized, prolog_s) )

                c = nlp_test_parser.parse_line_clause_body(prolog_s)
                # logging.debug( "Parse result: %s" % c)

                # logging.debug( "Searching for c: %s" % c )

                self.nlp_test_engine.reset_utterances()
                self.nlp_test_engine.reset_actions()
                solutions = self.nlp_test_engine.search(c)

                if len(solutions) == 0:
                    raise PrologError ('nlp_test: %s no solution found.' % clause.location)
            
                # print "round %d utterances: %s" % (round_num, repr(nlp_test_engine.get_utterances())) 

                # check actual utterances vs expected one

                test_in, test_out, test_actions = rounds[round_num]

                utterance_matched = False
                actual_out = ''
                utts = self.nlp_test_engine.get_utterances()

                if len(utts) > 0:
                    for utt in utts:
                        actual_out = ' '.join(tokenize(utt['utterance'], utt['lang']))
                        if actual_out == test_out:
                            utterance_matched = True
                            break
                else:
                    utterance_matched = len(test_out) == 0

                if utterance_matched:
                    if len(utts) > 0:
                        logging.info("nlp_test: %s round=%3d *** UTTERANCE MATCHED!" % (clause.location, round_num))
                else:
                    raise PrologError (u'nlp_test: %s round=%3d actual utterance \'%s\' did not match expected utterance \'%s\'.' % (clause.location, round_num, actual_out, test_out))
                
                # check actions

                if len(test_actions)>0:

                    # print repr(test_actions)

                    actions_matched = True
                    acts = self.nlp_test_engine.get_actions()
                    for action in test_actions:
                        for act in acts:
                            # print "    check action match: %s vs %s" % (repr(action), repr(act))
                            if action == act:
                                break
                        if action != act:
                            actions_matched = False
                            break

                    if actions_matched:
                        logging.info("nlp_test: %s round=%3d *** ACTIONS MATCHED!" % (clause.location, round_num))
                        
                    else:
                        raise PrologError (u'nlp_test: %s round=%3d ACTIONS MISMATCH.' % (clause.location, round_num))

                round_num += 1

    def set_context_default(self, clause):

        solutions = self.nlp_test_engine.search(clause)

        # print "set_context_default: solutions=%s" % repr(solutions)

        if len(solutions) != 1:
            raise PrologError ('set_context_default: need exactly one solution.')

        args = clause.head.args

        name  = args[0].s
        key   = args[1].name

        value = args[2]
        if isinstance (value, Variable):
            value = solutions[0][value.name]

        value = unicode(value)

        self.db.set_context_default(name, key, value)

    def do_compile (self, pl_fn, module_name):

        # quick source line count for progress output below

        linecnt = 0
        with codecs.open(pl_fn, encoding='utf-8', errors='ignore', mode='r') as f:
            while f.readline():
                linecnt += 1
        logging.info("%s: %d lines." % (pl_fn, linecnt))

        # setup compiler / test environment

        self.db         = LogicDB(self.session)

        parser          = PrologParser()

        self.nlp_macros = {}
        src             = None
        first           = True

        self.nlp_test_engine = PrologAIEngine(self.db)
        self.nlp_test_engine.set_trace(self.trace)
        self.nlp_test_engine.set_context_name('test')

        with codecs.open(pl_fn, encoding='utf-8', errors='ignore', mode='r') as f:
            parser.start(f, pl_fn)

            while parser.cur_sym != SYM_EOF:
                clauses = parser.clause()

                if first:
                    self.db.clear_module(module_name)
                    first = False

                for clause in clauses:
                    logging.debug(u"%7d / %7d (%3d%%) > %s" % (parser.cur_line, linecnt, parser.cur_line * 100 / linecnt, unicode(clause)))

                    # compiler directive?

                    if clause.head.name == 'nlp_macro':
                        self.nlp_macro(clause)

                    elif clause.head.name == 'nlp_gen':
                        self.nlp_gen(module_name, clause)

                    elif clause.head.name == 'nlp_test':
                        if self.run_tests:
                            self.nlp_test(clause)

                    elif clause.head.name == 'set_context_default':
                        self.set_context_default(clause)

                    else:
                        self.db.store (module_name, clause)

                if parser.comment_pred:

                    self.db.store_doc (module_name, parser.comment_pred, parser.comment)

                    parser.comment_pred = None
                    parser.comment = ''

        logging.info("Compilation succeeded.")
