# -*- coding: utf-8 -*-
"""강의 1~3일차 유물 사진을 해당 섹션 갤러리에 추가하고 출처 목록을 갱신해요. add_day03.py를 먼저 실행한 뒤 쓰면 돼요. 여러 번 실행해도 결과가 같아요."""
import io, os, re, json, urllib.parse
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'day01', 'index.html')
META = {m['k']: m for m in json.load(io.open(os.path.join(ROOT, 'tools', 'photos2_meta.json'), encoding='utf-8'))}
# (섹션 id, 사진 키, 캡션)
PLACE = [
 ('pre', 'dongsam', '부산 동삼동 패총(조개무지, 신석기)'),
 ('pre', 'jeongmun', '다뉴세문경 계열 청동 거울(정문경, 청동기)'),
 ('goguryeo', 'seokchon', '서울 석촌동 고분군(백제 초기 돌무지무덤)'),
 ('goguryeo', 'hou', '호우명 그릇(경주 호우총, 광개토대왕 관련)'),
 ('goguryeo', 'gangseo', '강서대묘 현무(고구려 사신도)'),
 ('baekje', 'sataek', '사택지적비(백제)'),
 ('unified', 'jangdo', '완도 장도(장보고의 청해진 터)'),
 ('culture', 'hyecho', '왕오천축국전(혜초)'),
 ('mid', 'samguk_yusa', '삼국유사(승려 일연)'),
 ('mongol', 'cheoin', '용인 처인성(김윤후, 2차 침입)'),
 ('mongol', 'yongjang', '진도 용장성(삼별초)'),
]
STAR = None
s = io.open(P, encoding='utf-8').read()


def fig(k, cap):
    m = META[k]
    return ('<figure class="ph"><a href="img/%s.jpg" target="_blank" rel="noopener"><img src="img/%s.jpg" alt="%s" loading="lazy" width="%d" height="%d"></a><figcaption>%s</figcaption></figure>'
            % (k, k, cap, m['w'], m['h'], cap))


for sid, k, cap in PLACE:
    a = s.index('<section class="sec" id="%s"' % sid)
    e = s.index('</section>', a)
    sec = s[a:e]
    if 'img/%s.jpg' % k in sec:
        continue
    g = sec.rfind('</div></article>')
    if '<div class="gal">' in sec and g > sec.index('<div class="gal">'):
        sec = sec[:g] + fig(k, cap) + sec[g:]
    else:
        sec += '<article class="card figc"><h3>관련 유물·유적 사진</h3><div class="gal">%s</div></article>' % fig(k, cap)
    s = s[:a] + sec + s[e:]

# 출처
for sid, k, cap in PLACE:
    m = META[k]
    if '데이터' in m['title'] or ('File:%s' % urllib.parse.quote(m['title'][5:].replace(' ', '_'), safe='()_.-,')) in s:
        continue
    li = '<li><b>%s</b> — %s · %s · <a href="https://commons.wikimedia.org/wiki/%s" target="_blank" rel="noopener">원본(Wikimedia Commons)</a></li>' % (
        cap, re.sub(r'(Unknown author)+', '작자 미상', m['artist']) or '작자 미상', m['lic'], urllib.parse.quote(m['title'].replace(' ', '_'), safe=':()_.-,'))
    s = s.replace('</ol></details><footer>', li + '</ol></details><footer>', 1)
n = s.count('<figure class="ph">')
s = re.sub(r'사진 · 지도 출처 \(\d+장\)', '사진 · 지도 출처 (%d장)' % n, s, count=1)
io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('사진 총', n, '장')
