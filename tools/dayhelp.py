# -*- coding: utf-8 -*-
"""일차별 생성 스크립트(add_dayNN.py)가 함께 쓰는 마크업 도우미. ★는 강사가 직접 강조한 항목."""
import io, os, re, json
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, 'day01', 'img')
META = {m['k']: m for m in json.load(io.open(os.path.join(ROOT, 'tools', 'photos2_meta.json'), encoding='utf-8'))}
STAR = '<em class="s" aria-label="중요"></em>'
USED = []


def fx(t):
    t = t.replace('★', STAR)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'\(\((.+?)\)\)', r'<span class="par">(\1)</span>', t)
    return t


def li(t):
    return '<li class="%s">%s</li>' % ('st' if t.startswith('★') else '', fx(t))


def pts(items):
    return '<ul class="pts">' + ''.join(li(i) for i in items) + '</ul>'


def note(t):
    return '<p class="note">%s</p>' % fx(t)


def table(head, rows):
    out = '<div class="tbwrap"><table class="tb"><thead><tr>' + ''.join('<th>%s</th>' % h for h in head) + '</tr></thead><tbody>'
    for r in rows:
        st = any('★' in c for c in r)
        out += '<tr class="%s">' % ('sti' if st else '') + ''.join('<td>%s</td>' % fx(c) for c in r) + '</tr>'
    return out + '</tbody></table></div>'


def kw(rows):
    out = '<div class="kwwrap"><table class="kw"><thead><tr><th>이 표현이 나오면</th><th>정답</th></tr></thead><tbody>'
    for k, a, st in rows:
        out += '<tr class="%s"><td class="k">%s</td><td class="a"><b>%s%s</b></td></tr>' % ('st' if st else '', fx(k), STAR if st else '', fx(a))
    return out + '</tbody></table></div>'


def card(title, body, cls='', tag=None):
    t = '<span class="tag">%s</span>' % tag if tag else ''
    return '<article class="card%s"><h3>%s%s</h3>%s</article>' % ((' ' + cls) if cls else '', fx(title), t, body)


def sec(sid, era, h2, lead, cards):
    return ('<section class="sec" id="%s"><header class="sh"><span class="era">%s</span><h2>%s</h2><p class="lead">%s</p></header>%s</section>\n'
            % (sid, era, h2, fx(lead), ''.join(cards)))


def arts(items):
    """(키, 이름, 시기, [특징]) 목록 → 사진 + 특징 목록."""
    out = ''
    for k, name, era, feats in items:
        f = os.path.join(IMG, k + '.jpg') if k else ''
        if k and os.path.exists(f):
            with Image.open(f) as im:
                w, h = im.size
            USED.append((k, name))
            ph = '<a class="aph" href="img/%s.jpg" target="_blank" rel="noopener"><img src="img/%s.jpg" alt="%s" loading="lazy" width="%d" height="%d"></a>' % (k, k, name, w, h)
        else:
            ph = '<div class="aph nop">사진 없음</div>'
        out += '<div class="art">%s<div class="abody"><h4>%s<span class="par">(%s)</span></h4>%s</div></div>' % (ph, name, era, pts(feats))
    return out
