# -*- coding: utf-8 -*-
"""암기 코드를 새 디자인으로 다시 만들어요.
1) 본문 곳곳의 옛 '타일 보드'를 새 코드 카드(compact)로 바꾸고
2) 책 끝에 '암기 코드 총정리' 섹션을 만들어요. 여러 번 실행해도 결과가 같아요.
실행 순서: add_day03.py → add_photos2.py → add_artifacts.py → add_codes.py → restyle_day01_toc.py"""
import io, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from codes_data import C, E
import codes_goryeo  # noqa: F401  (고려 코드 덮어쓰기)
import codes_day04  # noqa: F401  (Day-04 코드)
import codes_day05  # noqa: F401  (Day-05 코드)
import codes_day06  # noqa: F401  (Day-06 코드)
import codes_day07  # noqa: F401  (Day-07 코드)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'day01', 'index.html')
STAR = '<em class="s" aria-label="중요"></em>'


def esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def phrase(t):
    return re.sub(r'\{(.+?)\}', r'<mark class="hl">\1</mark>', esc(t))


def mapul(m):
    out = '<ul class="cc-map">'
    for k, name, desc, st in m:
        d = '<span>%s</span>' % esc(desc) if desc else ''
        out += '<li class="%s"><b>%s</b><div><strong>%s</strong>%s</div></li>' % ('st' if st else '', esc(k), esc(name), d)
    return out + '</ul>'


def chunks(gs):
    out = '<div class="cc-chunks">'
    for t, items in gs:
        lis = ''.join('<li class="%s"><strong>%s</strong>%s</li>' % ('st' if st else '', esc(n), ('<span>%s</span>' % esc(d)) if d else '') for n, d, st in items)
        out += '<div class="cc-ch"><div class="cc-ct">%s</div><ul>%s</ul></div>' % (esc(t), lis)
    return out + '</div>'


def body(c):
    return chunks(c['groups']) if c.get('groups') else mapul(c['map'])


def inline(c):
    return '<div class="cci"><p class="cc-phrase">%s</p>%s</div>' % (phrase(c['phrase']), mapul(c['map']))


def card(c):
    star = STAR if c.get('star') else ''
    return ('<article class="card cc"><h3>%s%s<span class="tag">%s</span></h3><p class="cc-phrase">%s</p>%s<p class="cc-story">%s</p></article>'
            % (star, esc(c['name']), c.get('tag', E[c['era']]), phrase(c['phrase']), body(c), esc(c['story'])))


s = io.open(P, encoding='utf-8').read()

# 1) 본문 보드 교체
TILE = r'<div class="t[^"]*"><b[^>]*>.*?</b><i>.*?</i></div>'
done = 0
for c in C:
    for cap in c.get('inline', []):
        pat = re.compile(r'<div class="board"><div class="bcap">' + re.escape(cap) + r'</div>(?:<div class="row"[^>]*>(?:' + TILE + r')+</div>)+</div>', re.S)
        s, n = pat.subn(lambda m: inline(c), s)
        done += n

# 1-2) 고려 코드를 각 섹션 머리에 배치
s = re.sub(r'<article class="card cc cc-top" data-code="[^"]+">.*?</article>', '', s, flags=re.S)
placed = 0
for c in C:
    sid = c.get('place')
    if not sid or sid == 'hs':
        continue
    a = s.find('<section class="sec" id="%s"' % sid)
    if a < 0:
        continue
    h = s.index('</header>', a) + len('</header>')
    s = s[:h] + card(c).replace('<article class="card cc">', '<article class="card cc cc-top" data-code="%s">' % c['id'], 1) + s[h:]
    placed += 1

# 2) 총정리 섹션
a = s.find('<div class="dayhead" id="codes-head">')
if a >= 0:
    e = s.index('<p class="empty hide" id="empty">')
    s = s[:a] + s[e:]
html = '<div class="dayhead" id="codes-head"><span class="dn">부록</span><span class="dt">암기 코드 총정리</span></div>\n'
html += ('<section class="sec" id="codes"><header class="sh"><span class="era">1~7일차 암기 코드</span><h2>강사가 알려 준 암기 코드 한눈에</h2>'
         '<p class="lead">코드는 문장의 <mark class="hl">표시된 글자</mark>만 이어 읽으면 돼요. 글자마다 무엇을 가리키는지 바로 아래에 짝지어 뒀고, 별은 강사가 특히 강조한 항목이에요. 강의에 나오지 않은 코드는 넣지 않았어요.</p></header>')
for i, name in enumerate(E):
    cs = [c for c in C if c['era'] == i]
    if not cs:
        continue
    html += '<h3 class="cc-era">%s<small>%d개</small></h3><div class="cc-grid">%s</div>' % (name, len(cs), ''.join(card(c) for c in cs))
html += '</section>\n'
e = s.index('<p class="empty hide" id="empty">')
s = s[:e] + html + s[e:]

# 3) CSS
CSS = '''/* 암기 코드 */
mark.hl { background: linear-gradient(transparent 52%, color-mix(in srgb, var(--sticky) 85%, transparent) 52%); color: inherit; font-weight: 900; padding: 0 1px; }
.cc-phrase { margin: 6px 0 14px; font: 800 clamp(18px, 2.2vw, 22px)/1.6 var(--f-body); letter-spacing: .01em; text-wrap: balance; }
.cc-map { list-style: none; margin: 0; padding: 0; display: grid; gap: 7px; }
.cc-map li { display: grid; grid-template-columns: auto minmax(0, 1fr); gap: 10px; align-items: start; }
.cc-map li b { position: relative; display: grid; place-items: center; min-width: 34px; height: 34px; padding: 0 7px; border-radius: 9px; background: var(--sticky); color: var(--sticky-fg); font: 900 15px var(--f-body); box-shadow: 0 2px 0 color-mix(in srgb, var(--sticky-fg) 16%, transparent); }
.cc-map li.st b::after { content: ""; position: absolute; top: -7px; right: -7px; width: 16px; height: 16px; background: var(--star); -webkit-mask: var(--star-mask) center / contain no-repeat; mask: var(--star-mask) center / contain no-repeat; filter: drop-shadow(0 1px 0 rgba(0,0,0,.25)); }
.cc-map li strong { font-weight: 700; }
.cc-map li span { display: block; font-size: 13.5px; line-height: 1.5; color: var(--muted); }
.cc-story { margin: 14px 0 0; padding: 10px 12px; border-radius: 10px; background: var(--sheet); font-size: 14px; line-height: 1.65; }
.cci { margin: 12px 0; padding: 14px 16px 16px; border: 1.5px dashed var(--line); border-radius: 12px; background: color-mix(in srgb, var(--sheet) 55%, transparent); }
.cci .cc-phrase { margin-top: 0; }
.cci .cc-map { grid-template-columns: repeat(auto-fill, minmax(min(100%, 230px), 1fr)); gap: 8px 14px; }
.cc-era { display: flex; align-items: baseline; gap: 10px; margin: 28px 0 12px; padding-bottom: 6px; border-bottom: 2px solid var(--fg); font: 800 18px var(--f-body); }
.cc-era small { font: 500 12.5px var(--f-body); color: var(--muted); }
.cc-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 320px), 1fr)); gap: 16px; align-items: start; }
.cc-grid .card { margin: 0; }
.cc-chunks { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 220px), 1fr)); gap: 22px 12px; padding-top: 12px; }
.cc-ch { padding: 18px 12px 12px; border: 1.5px solid var(--line); border-radius: 12px; position: relative; }
.cc-ct { position: absolute; top: -13px; left: 10px; padding: 2px 12px; border-radius: 4px 4px 12px 4px; background: var(--sticky); color: var(--sticky-fg); font: 900 15px var(--f-body); transform: rotate(-1.5deg); box-shadow: 2px 3px 0 color-mix(in srgb, var(--sticky-fg) 14%, transparent); max-width: calc(100% - 20px); }
.cc-ch ul { list-style: none; margin: 0; padding: 0; display: grid; gap: 8px; }
.cc-ch li { position: relative; padding-left: 12px; font-size: 14px; line-height: 1.55; }
.cc-ch li::before { content: ""; position: absolute; left: 0; top: .62em; width: 5px; height: 5px; border-radius: 50%; background: var(--marker); }
.cc-ch li strong { font-weight: 800; }
.cc-ch li span { display: block; font-size: 13px; color: var(--muted); }
.cc-ch li.st strong::before { content: ""; display: inline-block; width: 14px; height: 14px; margin-right: 4px; vertical-align: -2px; background: var(--star); -webkit-mask: var(--star-mask) center / contain no-repeat; mask: var(--star-mask) center / contain no-repeat; }
.card.cc-top { margin-bottom: 18px; }
'''
MARK = '/* 암기 코드 */'
if MARK in s:
    s = re.sub(re.escape(MARK) + r'.*?(?=/\* [^*]+\*/|</style>)', lambda m: CSS, s, count=1, flags=re.S)
else:
    s = s.replace('</style>', CSS + '</style>', 1)
io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('섹션 머리 배치', placed, '개 / 본문 보드 교체', done, '곳, 총정리 코드', len(C), '개')
