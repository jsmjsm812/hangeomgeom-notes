# -*- coding: utf-8 -*-
"""Day-08(흥선 대원군 ~ 국권 피탈) 강의 노트를 day01/index.html에 붙여요. 여러 번 실행해도 결과가 같아요.
별(★)은 강사가 직접 '시험에 많이 나온다 / 아주·너무 중요하다 / 3점 / 반드시'라고 강조한 표현에만 달았어요.
사실은 자동 자막이 아니라 실제 역사(조약문·연도·인물)와 대조해 확정했어요."""
import io, os, re, sys, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dayhelp
from dayhelp import ROOT, META, USED
import day08_a, day08_b, day08_c

P = os.path.join(ROOT, 'day01', 'index.html')
html = ''.join(day08_a.S + day08_b.S + day08_c.S)
band = '<div class="dayhead" id="day8"><span class="dn">Day-08</span><span class="dt">흥선 대원군 · 개항 · 갑오개혁 · 대한제국 · 국권 피탈</span></div>\n'
block = band + html

s = io.open(P, encoding='utf-8').read()
a = s.find('<div class="dayhead" id="day8">')
tail = [x for x in (s.find('<div class="dayhead" id="codes-head">', max(a, 0)), s.find('<p class="empty hide" id="empty">', max(a, 0))) if x >= 0]
e = min(tail)
if a >= 0:
    s = s[:a] + block + s[e:]
else:
    e = min(x for x in (s.find('<div class="dayhead" id="codes-head">'), s.find('<p class="empty hide" id="empty">')) if x >= 0)
    s = s[:e] + block + s[e:]

# 표지 문구
s = re.sub(r'<p class="sub">.*?</p>',
           '<p class="sub">강의를 일차별·시대 순서로 이어서 정리하고 있어요. 지금은 선사 시대부터 고대·고려·조선(Day-03~07)을 거쳐 흥선 대원군의 집권, 개항, 갑신정변, 동학 농민 운동, 갑오개혁, 대한제국, 러일 전쟁과 국권 피탈(Day-08)까지 들어 있고, 다음 일차가 나올 때마다 이 한 페이지에 이어 붙여요.</p>',
           s, count=1, flags=re.S)

# 사진 출처
for k, name in USED:
    m = META.get(k)
    if not m:
        continue
    q = urllib.parse.quote(m['title'].replace(' ', '_'), safe=':()_.-,')
    if q in s:
        continue
    artist = re.sub(r'(Unknown author)+', '작자 미상', m['artist']) or '작자 미상'
    li_ = '<li><b>%s</b> — %s · %s · <a href="https://commons.wikimedia.org/wiki/%s" target="_blank" rel="noopener">원본(Wikimedia Commons)</a></li>' % (name, artist, m['lic'], q)
    s = s.replace('</ol></details><footer>', li_ + '</ol></details><footer>', 1)
n = len(set(re.findall(r'<img src="img/([^"]+)"', s)))
s = re.sub(r'사진 · 지도 출처 \(\d+장\)', '사진 · 지도 출처 (%d장)' % n, s, count=1)
io.open(P, 'w', encoding='utf-8', newline='\n').write(s)

# 허브 카드 문구
hp = os.path.join(ROOT, 'index.html')
h = io.open(hp, encoding='utf-8').read()
h = re.sub(r'강의 노트 \(Day-01 ~ 0\d, 계속 추가\)', '강의 노트 (Day-01 ~ 08, 계속 추가)', h)
if '대한제국과 국권 피탈' not in h:
    h = re.sub(r'(조선의 경제·사회·문화)', r'\1, 개항·갑오개혁·대한제국과 국권 피탈', h, count=1)
io.open(hp, 'w', encoding='utf-8', newline='\n').write(h)
print('Day-08 삽입 완료, 별 표시 수:', block.count('class="s"'), '/ 사진', len(USED), '장')
