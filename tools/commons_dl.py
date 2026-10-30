# -*- coding: utf-8 -*-
"""Commons 사진을 day01/img에 내려받고 tools/photos2_meta.json에 출처를 기록해요.
사용: python commons_dl.py items.json   (items: [[키, 캡션, "File:제목"], ...])"""
import json, urllib.request, urllib.parse, re, html, time, sys, os
H = {'User-Agent': 'notes-bot/1.0 (study)'}
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
items = json.load(open(sys.argv[1], encoding='utf-8'))
mp = os.path.join(ROOT, 'tools', 'photos2_meta.json')
meta = json.load(open(mp, encoding='utf-8'))
for k, cap, t in items:
    if os.path.exists(os.path.join(ROOT, 'day01', 'img', k + '.jpg')) and any(x['k'] == k for x in meta):
        print(k, 'skip'); continue
    time.sleep(8)
    u = 'https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode({'action': 'query', 'titles': t, 'prop': 'imageinfo', 'iiprop': 'url|extmetadata', 'iiurlwidth': 720, 'format': 'json'})
    try:
        p = list(json.load(urllib.request.urlopen(urllib.request.Request(u, headers=H)))['query']['pages'].values())[0]['imageinfo'][0]
        m = p['extmetadata']
        g = lambda n: re.sub('<[^>]+>', '', html.unescape(m.get(n, {}).get('value', ''))).strip()
        time.sleep(5)
        open(os.path.join(ROOT, 'day01', 'img', k + '.jpg'), 'wb').write(urllib.request.urlopen(urllib.request.Request(p['thumburl'], headers=H)).read())
        meta = [x for x in meta if x['k'] != k] + [dict(k=k, cap=cap, title=t, artist=g('Artist'), lic=g('LicenseShortName'), w=p['thumbwidth'], h=p['thumbheight'])]
        print(k, '|', g('Artist')[:40], '|', g('LicenseShortName'), '|', p['thumbwidth'], p['thumbheight'], flush=True)
    except Exception as e:
        print(k, 'FAIL', e, flush=True)
    json.dump(meta, open(mp, 'w', encoding='utf-8'), ensure_ascii=False)
