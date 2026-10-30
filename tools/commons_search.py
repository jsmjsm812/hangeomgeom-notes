# -*- coding: utf-8 -*-
"""Wikimedia Commons 파일 검색. 사용: python commons_search.py "검색어" ["검색어2" ...]"""
import sys, json, urllib.request, urllib.parse, time
H = {'User-Agent': 'notes-bot/1.0 (study)'}
for q in sys.argv[1:]:
    time.sleep(3)
    u = 'https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode({'action': 'query', 'list': 'search', 'srsearch': q, 'srnamespace': 6, 'srlimit': 5, 'format': 'json'})
    r = None
    for a in range(4):
        try:
            r = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=H)))
            break
        except Exception:
            time.sleep(15)
    print('##', q)
    for x in (r or {}).get('query', {}).get('search', []):
        print('  ', x['title'])
