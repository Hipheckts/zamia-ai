#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import logging
import rdflib
from rdflib.plugins.sparql.parserutils import CompValue

from nltools.tokenizer    import tokenize
from nltools.misc         import limit_str

MAX_NER_RESULTS = 5

ner_dict   = {} # lang -> class -> token -> entity -> [idx1, idx2, ...]

def ner_learn(lang, cls, entities, labels):

    global ner_dict

    # import pdb; pdb.set_trace()

    if not lang in ner_dict:
        ner_dict[lang] = {}

    if not cls in ner_dict[lang]:
        ner_dict[lang][cls] = {}

    nd = ner_dict[lang][cls]

    for i, entity in enumerate(entities):

        label = labels[i]

        for j, token in enumerate(tokenize(label, lang=lang)):

            if not token in nd:
                nd[token] = {}

            if not entity in nd[token]:
                nd[token][entity] = set([])

            nd[token][entity].add(j)

            # logging.debug ('ner_learn: %4d %s %s: %s -> %s %s' % (i, entity, label, token, cls, lang))

    cnt = 0
    for token in nd:
        # import pdb; pdb.set_trace()
        # s1 = repr(nd[token])
        # s2 = limit_str(s1, 10)
        logging.debug ('ner_learn: nd[%-20s]=%s' % (token, limit_str(repr(nd[token]), 80)))
        cnt += 1
        if cnt > 10:
            break


    return True

def ner(lang, ias, cls, tstart, tend):

    global ner_dict

    nd = ner_dict[lang][cls]

    tokens = ias['tokens']

    #
    # start scoring
    #

    max_scores = {}

    for tstart in range (tstart-1, tstart+2):
        if tstart <0:
            continue

        for tend in range (tend-1, tend+2):
            if tend > len(tokens):
                continue
  
            scores = {}

            for tidx in range(tstart, tend):

                toff = tidx-tstart

                # logging.debug('tidx: %d, toff: %d [%d - %d]' % (tidx, toff, tstart, tend))

                token = tokens[tidx]
                if not token in nd:
                    # logging.debug('token %s not in nd %s %s' % (repr(token), repr(lang), repr(cls)))
                    continue

                for entity in nd[token]:

                    if not entity in scores:
                        scores[entity] = 0.0

                    for eidx in nd[token][entity]:
                        points = 2.0-abs(eidx-toff)
                        if points>0:
                            scores[entity] += points

            logging.debug('scores: %s' % repr(scores))

            for entity in scores:
                if not entity in max_scores:
                    max_scores[entity] = scores[entity]
                    continue
                if scores[entity]>max_scores[entity]:
                    max_scores[entity] = scores[entity]

    res = []
    cnt = 0

    # for entity in max_scores:

    for entity, max_score in sorted(max_scores.iteritems(), key=lambda x: x[1], reverse=True):

        res.append((entity, max_score))

        cnt += 1
        if cnt > MAX_NER_RESULTS:
            break

    return res

def ner_best(ner_res, ias):
    # FIXME: provide hook(s) for scoring functions
    return ner_res[0]

