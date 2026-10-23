# -*- coding: utf-8 -*-
"""강의 노트(day01/index.html)의 왼쪽 목차를 교재처럼 '부 → 장 번호' 체계로 정리해요. 여러 번 실행해도 결과가 같아요."""
import io, re, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'day01', 'index.html')
s = io.open(P, encoding='utf-8').read()

GROUPS = [
    (None, '시작하기', '시험 구조와 기출 패턴', [('orient', '시험 안내'), ('patterns', '기출 풀이 패턴')]),
    ('제1부', '선사 · 고조선', '구석기 ~ 기원전 108년', [('pre', '선사 시대'), ('gojoseon', '고조선'), ('nations', '철기 시대의 여러 나라')]),
    ('제2부', '삼국 시대', '기원전 1세기 ~ 7세기', [('common', '삼국의 공통점'), ('goguryeo', '고구려'), ('baekje', '백제'), ('silla', '신라'), ('gaya', '가야')]),
    ('제3부', '삼국 통일', '642년 ~ 676년', [('years', '통일 과정의 연도'), ('recap', '통일 과정 총정리')]),
    ('제4부', '남북국 시대', '7세기 말 ~ 10세기 초', [('unified', '통일신라와 후삼국'), ('balhae', '발해')]),
    ('제5부', '고대의 경제 · 사회 · 문화', '삼국 ~ 남북국', [('econ', '경제와 사회'), ('culture', '문화'), ('artifacts', '사진으로 보는 문화유산')]),
    ('제6부', '후삼국 · 고려 초기', '918년 ~ 11세기', [('hs', '후삼국 통일'), ('goryeo', '고려 시대 전체 흐름'), ('taejo', '태조 왕건'), ('early', '혜종 ~ 성종'), ('khitan', '목종 · 현종과 거란')]),
    ('제7부', '고려의 제도', '중앙 · 지방 · 군사', [('system', '정치 기구와 지방·군사 제도')]),
    ('제8부', '고려 중기 · 무신 집권기', '12세기 ~ 13세기', [('mid', '문벌의 시대'), ('mushin', '무신 집권기')]),
    ('제9부', '몽골 · 원 간섭 · 멸망', '13세기 ~ 1392년', [('mongol', '몽골 침입'), ('won', '원 간섭기'), ('end', '공민왕과 고려 멸망')]),
]

toc, mnav, n = '', '', 0
for part, title, period, items in GROUPS:
    pn = f'<span class="pn">{part}</span>' if part else ''
    toc += f'<li class="grp">{pn}{title}<small>{period}</small></li>'
    mnav += f'<li class="grpchip">{(part + " ") if part else ""}{title}</li>'
    for sid, label in items:
        if part: n += 1
        no = f'<span class="no">{n}</span>' if part else '<span class="no">·</span>'
        toc += f'<li><a href="#{sid}" data-id="{sid}">{no}<span class="tl">{label}</span></a></li>'
        mnav += f'<li><a href="#{sid}">{label}</a></li>'

s, c1 = re.subn(r'(<aside class="toc"[^>]*>.*?)<ol>.*?</ol>', lambda m: m.group(1) + '<ol>' + toc + '</ol>', s, count=1, flags=re.S)
s, c2 = re.subn(r'(<nav class="mnav"[^>]*><ul>).*?(</ul></nav>)', lambda m: m.group(1) + mnav + m.group(2), s, count=1, flags=re.S)
assert c1 == 1 and c2 == 1, (c1, c2)

CSS = '''/* 교재식 목차 */
.toc ol { border-left: 0; gap: 0; }
.toc li.grp { display: block; margin: 20px 0 4px; padding: 0 0 5px 2px; border-bottom: 2px solid var(--fg); font: 800 14px/1.3 var(--f-body); letter-spacing: 0; color: var(--fg); }
.toc li.grp:first-child { margin-top: 0; }
.toc li.grp .pn { margin-right: 7px; color: var(--marker); }
.toc li.grp small { display: block; margin-top: 3px; font: 500 11.5px var(--f-body); color: var(--muted); }
.toc a { display: grid; grid-template-columns: 24px 1fr; gap: 4px; align-items: baseline; padding: 6px 8px 6px 2px; margin-left: 0; border-left: 0; border-bottom: 1px dotted var(--line); border-radius: 0; font-size: 14.5px; }
.toc a .no { font: 700 12.5px var(--f-body); color: var(--marker); text-align: center; }
.toc a.on { background: var(--sheet); font-weight: 700; box-shadow: inset 3px 0 0 var(--marker); padding-left: 8px; }
.toc a.on .no { margin-left: -6px; }
'''
MARK = '/* 교재식 목차 */'
if MARK in s:
    s = re.sub(re.escape(MARK) + r'.*?(?=/\* [^*]+\*/|</style>)', CSS, s, count=1, flags=re.S)
else:
    s = s.replace('</style>', CSS + '</style>', 1)
io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('목차 항목', n, '개 정리 완료')
