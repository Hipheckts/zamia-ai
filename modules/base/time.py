#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#
# time and date (pretty crude so far, but we have to get started somewhere...)
#

# #
# # time/date calculations
# #
# 
# time_span(CT, today, TS, TE) :-
#     stamp_date_time(CT, date(Y,M,D,H,Mn,S,'local')),
#     date_time_stamp(date(Y,M,D, 0, 0, 0,'local'), TS),
#     date_time_stamp(date(Y,M,D,23,59,59,'local'), TE).
# 
# time_span(CT, tomorrow, TS, TE) :-
#     stamp_date_time(CT, date(Y,M,D,H,Mn,S,'local')),
#     date_time_stamp(date(Y,M,D + 1, 0, 0, 0,'local'), TS),
#     date_time_stamp(date(Y,M,D + 1,23,59,59,'local'), TE).
# 
# time_span(CT, dayAfterTomorrow, TS, TE) :-
#     stamp_date_time(CT, date(Y,M,D,H,Mn,S,'local')),
#     date_time_stamp(date(Y,M,D + 2, 0, 0, 0,'local'), TS),
#     date_time_stamp(date(Y,M,D + 2,23,59,59,'local'), TE).
# 
# time_span(CT, nextThreeDays, TS, TE) :-
#     stamp_date_time(CT, date(Y,M,D,H,Mn,S,'local')),
#     date_time_stamp(date(Y,M,D,H,Mn,S,'local'), TS),
#     date_time_stamp(date(Y,M,D+3,H,Mn,S,'local'), TE).
# 
# #
# # time strings
# #
# 
# time_label(CT, en, today,            "today").
# time_label(CT, en, tomorrow,         "tomorrow").
# time_label(CT, en, dayAfterTomorrow, "day after tomorrow").
# time_label(CT, en, nextThreeDays,    "in the next three days").
# 
# time_label(CT, de, today,            "heute").
# time_label(CT, de, tomorrow,         "morgen").
# time_label(CT, de, dayAfterTomorrow, "übermorgen").
# time_label(CT, de, nextThreeDays,    "in den nächsten drei Tagen").
# 
# transcribe_month(en,  1, 'january').
# transcribe_month(en,  2, 'feburary').
# transcribe_month(en,  3, 'march').
# transcribe_month(en,  4, 'april').
# transcribe_month(en,  5, 'may').
# transcribe_month(en,  6, 'june').
# transcribe_month(en,  7, 'july').
# transcribe_month(en,  8, 'august').
# transcribe_month(en,  9, 'september').
# transcribe_month(en, 10, 'october').
# transcribe_month(en, 11, 'november').
# transcribe_month(en, 12, 'december').
# 
# transcribe_month(de,  1, 'januar').
# transcribe_month(de,  2, 'feburar').
# transcribe_month(de,  3, 'märz').
# transcribe_month(de,  4, 'april').
# transcribe_month(de,  5, 'mai').
# transcribe_month(de,  6, 'juni').
# transcribe_month(de,  7, 'juli').
# transcribe_month(de,  8, 'august').
# transcribe_month(de,  9, 'september').
# transcribe_month(de, 10, 'oktober').
# transcribe_month(de, 11, 'november').
# transcribe_month(de, 12, 'dezember').
# 
# transcribe_date(en, dativ, TS, SCRIPT) :-
#     stamp_date_time(TS, date(Y,M,D,H,Mn,S,'local')),
#     transcribe_number(en, nominative, D, DS),
#     transcribe_month(en, M, MS),
#     SCRIPT is format_str('%s %s, %s', MS, DS, Y).
# 
# transcribe_date(de, dativ, TS, SCRIPT) :-
#     stamp_date_time(TS, date(Y,M,D,H,Mn,S,'local')),
#     transcribe_number(de, ord_gen, D, DS),
#     transcribe_month(de, M, MS),
#     SCRIPT is format_str('%s %s %s', DS, MS, Y).
# 
# #
# # time and dates
# #
# 
# before_noon(TS) :- stamp_date_time(TS,date(Y,M,D,H,MIN,S,'local')), H < 12.
# after_noon(TS) :- stamp_date_time(TS,date(Y,M,D,H,MIN,S,'local')), H >= 12.
# 
# before_evening(TS)  :- stamp_date_time(TS,date(Y,M,D,H,MIN,S,'local')), H < 18.
# % before_evening(now) :- get_time(T), before_evening(T).
# 
# after_evening(TS)   :- stamp_date_time(TS,date(Y,M,D,H,MIN,S,'local')), H >= 18.
# % after_evening(now)  :- get_time(T), after_evening(T).
# 
# % startTime(tomorrowAfternoon,X) :- date_time_stamp(date(2015,12,03,11,0,0,'local'),X).
# % endTime(tomorrowAfternoon,X)   :- date_time_stamp(date(2015,12,03,17,0,0,'local'),X).
# %  %future(TimeSpan) :- startTime(TimeSpan,StartTime), getTime(Now), Now <= StartTime.
# %  %future(TimeSpan) :- startTime(TimeSpan,StartTime), get_time(Now), Now =< StartTime.
# %  
# %  tomorrow(RefT,EvT) :- startTime(EvT,EvStartTime), 
# %                        stamp_date_time(EvStartTime,EvStartStamp,local), 
# %                        date_time_value('day',EvStartStamp,EvStartDay),
# %                        stamp_date_time(RefT,RefTStamp,local),
# %                        date_time_value('day',RefTStamp,RefTDay),
# %                        TomorrowDay is RefTDay + 1,
# %                        EvStartDay = TomorrowDay.
# %                      
# %  context_get(T) :- get_time(T).
# %  % context_get(get_time(Now)).
# %  
# 
# % startTime(tomorrowAfternoon,X) :- get_time(TS),
# %                                   stamp_date_time(TS,date(Y,M,D,H,MIN,S,'local')),
# %                                   D2 is D+1,
# %                                   date_time_stamp(date(Y,M,D2,12,0,0,'local'), X).
# 
# nlp_timespec(en, S, today)            :- hears(en, S, 'today').
# nlp_timespec(en, S, tomorrow)         :- hears(en, S, 'tomorrow').
# nlp_timespec(en, S, dayAfterTomorrow) :- hears(en, S, 'the day after tomorrow').
# nlp_timespec(en, S, nextThreeDays)    :- hears(en, S, 'the next three days').
# 
# nlp_timespec(de, S, today)            :- hears(de, S, 'heute').
# nlp_timespec(de, S, tomorrow)         :- hears(de, S, 'morgen').
# nlp_timespec(de, S, dayAfterTomorrow) :- hears(de, S, 'übermorgen').
# nlp_timespec(de, S, nextThreeDays)    :- hears(de, S, 'die nächsten drei Tage').
# 
# nlp_say_time(en, R, T_H,     1) :- says (en, R, "one minute past %(f1_hour)d"),!.
# nlp_say_time(en, R, T_H,     0) :- says (en, R, "exactly %(f1_hour)d o'clock"),!.
# nlp_say_time(en, R, T_H,    15) :- says (en, R, "a quarter past %(f1_hour)d"),!.
# nlp_say_time(en, R, T_H,    30) :- says (en, R, "half past %(f1_hour)d"),!.
# nlp_say_time(en, R, T_H, T_MIN) :- says (en, R, "%(f1_minute)d minutes past %(f1_hour)d").
# 
# nlp_say_date(en, R) :- says (en, R, "%(f1_wday_label)s %(f1_month_label)s %(f1_day)d, %(f1_year)d").

NLP_DAY_OF_THE_WEEK_LABEL = {
    'en': { 0: 'Monday',
            1: 'Tuesday',
            2: 'Wednesday',
            3: 'Thursday',
            4: 'Friday',
            5: 'Saturday',
            6: 'Sunday'},

    'de': { 0: 'Montag',
            1: 'Dienstag',
            2: 'Mittwoch',
            3: 'Donnerstag',
            4: 'Freitag',
            5: 'Samstag',
            6: 'Sonntag'} }


NLP_MONTH_LABEL = {
    'en': { 1: 'January',
            2: 'February',
            3: 'March',
            4: 'April',
            5: 'May',
            6: 'June',
            7: 'July',
            8: 'August',
            9: 'September',
           10: 'October',
           11: 'November',
           12: 'December'},

    'de': { 1: 'Januar',
            2: 'Februar',
            3: 'März',
            4: 'April',
            5: 'Mai',
            6: 'Juni',
            7: 'Juli',
            8: 'August',
            9: 'September',
           10: 'Oktober',
           11: 'November',
           12: 'Dezember'}}

