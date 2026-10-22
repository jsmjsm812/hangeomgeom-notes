# -*- coding: utf-8 -*-
"""강의 노트(day01/index.html)를 읽어서 '교재' 레이아웃(textbook/index.html)으로 다시 조판해요.
사용법: python tools/build_textbook.py   (저장소 루트에서)"""
import io, re, sys, os, html as _h
from copy import deepcopy
from lxml import html as LH

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'day01', 'index.html')
OUT = os.path.join(ROOT, 'textbook', 'index.html')
E = _h.escape

src = io.open(SRC, encoding='utf-8').read()
doc = LH.fromstring(src)
ORIG_CSS = re.search(r'<style>(.*?)</style>', src, re.S).group(1)

PARTS = [
    ('제1부', '시험 안내와 선사 · 고조선', ['orient', 'pre', 'gojoseon', 'nations']),
    ('제2부', '삼국 시대', ['common', 'goguryeo', 'baekje', 'silla', 'gaya']),
    ('제3부', '삼국 통일', ['years', 'recap']),
    ('제4부', '남북국 시대', ['unified', 'balhae']),
    ('제5부', '고대의 경제 · 사회 · 문화', ['econ', 'culture']),
]
APPX = ['patterns']
LABEL = {'orient': '시험 안내', 'pre': '선사 시대', 'gojoseon': '고조선', 'nations': '철기 시대의 여러 나라', 'common': '삼국 시대의 공통점',
         'goguryeo': '고구려', 'baekje': '백제', 'silla': '신라', 'gaya': '가야', 'years': '삼국 통일의 연도', 'recap': '삼국 통일 과정',
         'unified': '통일신라와 후삼국', 'balhae': '발해', 'econ': '고대의 경제와 사회', 'culture': '고대의 문화', 'patterns': '기출 풀이 패턴'}

# ---------- 문체: 강의 말투 → 교재 말투 ----------
FIX = [('이 강의는 심화에', '이 책은 심화에'), ('기본도 이 강의로', '기본도 이 책으로'), ('강의에서는 “팔고 사고”로 외워요', '암기 코드는 “팔고 사고”예요'),
       ('이 시간의 한 줄 정리', '한 줄 정리'), ('다음 시간', '다음 장'), ('예고:', '뒤에서 다룸:')]
EXACT = {'있어요': '있다', '없어요': '없다', '나와요': '나온다', '보여요': '보인다', '외워요': '외운다', '달라요': '다르다', '많아요': '많다', '나눠요': '나눈다',
         '써요': '쓴다', '잡아요': '잡는다', '움직여요': '움직인다', '들어와요': '들어온다', '따라와요': '따라온다', '돼요': '된다', '해요': '한다', '같아요': '같다',
         '두세요': '둔다', '보세요': '본다', '않아요': '않는다', '나요': '난다', '추천해요': '추천한다', '시작해요': '시작한다'}

def hang_batchim(ch):
    c = ord(ch) - 0xAC00
    return (c % 28) if 0 <= c < 11172 else 0

def conv_word(w):
    """w 는 '요' 로 끝나는 어절의 일부(앞 1~4글자 + 요). 변환 못 하면 None"""
    if w.endswith('아니에요'): return w[:-4] + '아니다'
    if w.endswith('이에요'): return w[:-3] + '이다'
    if w.endswith('예요'): return w[:-2] + '이다'
    for k, v in EXACT.items():
        if w.endswith(k): return w[:-len(k)] + v
    if w.endswith('세요'):
        stem = w[:-2]
        if not stem: return None
        last = stem[-1]
        if hang_batchim(last) == 0:
            return stem[:-1] + chr(ord(last) + 4) + '다'
        return stem + '는다'
    if len(w) >= 3 and w.endswith('어요') and hang_batchim(w[-3]) == 20: return w[:-2] + '다'   # 었어요 · 했어요 · 됐어요 …
    if len(w) >= 3 and w.endswith('아요') and hang_batchim(w[-3]) == 20: return w[:-2] + '다'
    if w.endswith('해요'): return w[:-2] + '한다'
    if w.endswith('돼요'): return w[:-2] + '된다'
    if w.endswith('와요'): return w[:-2] + '온다'
    if w.endswith('여요'): return w[:-2] + '인다'
    if w.endswith('져요'): return w[:-2] + '진다'
    if w.endswith('눠요'): return w[:-2] + '눈다'
    if w.endswith('워요'): return w[:-2] + '운다'
    return None

def fix_ending(s):
    for a, b in FIX: s = s.replace(a, b)
    def rep(m):
        w = m.group(1)
        if w.endswith('서동요'): return m.group(0)
        c = conv_word(w)
        return (c + m.group(2)) if c else m.group(0)
    return re.sub(r'([가-힣]{1,5}요)((?:[.)”"’])*(?=<|\s|$))', rep, s)

def jamo_ini(ch):
    c = ord(ch) - 0xAC00
    if not 0 <= c < 11172: return None
    return 'ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ'[c // 588]

# ---------- 장 · 절 만들기 ----------
def inner(e):
    return (e.text or '') + ''.join(LH.tostring(c, encoding='unicode') for c in e)

def clean_title(t):
    t = re.sub(r'\s*[—-]\s*“[^”]*”', '', t)
    return re.sub(r'\s+', ' ', t).strip()

secs = {s.get('id'): s for s in doc.xpath('//section[@class="sec"]')}
chap_no = {}
n = 0
for _, _, ids in PARTS:
    for i in ids:
        n += 1; chap_no[i] = n
for i in APPX: chap_no[i] = 'A'

def card_title(card):
    h = card.find('h3')
    tag = h.find('.//span[@class="tag"]')
    t = (h.text or '') + ''.join((c.text or '') + (c.tail or '') for c in h if c is not tag)
    return clean_title(t), (tag.text_content().strip() if tag is not None else '')

def build_chapter(sid):
    sec = secs[sid]; num = chap_no[sid]
    label = LABEL[sid]; h2 = sec.find('.//h2').text_content().strip()
    lead = sec.find('.//p[@class="lead"]').text_content().strip()
    cards = sec.xpath('./article')
    figc = 0; phc = 0; tbc = 0
    subs = []; objs = []; stars = []; qa = []
    terms = []
    for k, card in enumerate(cards, 1):
        title, tag = card_title(card)
        figc_before = figc
        body = []
        is_kw = card.find('.//table[@class="kw"]') is not None
        is_ph = card.find('.//div[@class="gal"]') is not None
        for ch in card:
            if ch.tag == 'h3': continue
            cl = ch.get('class') or ''
            if ch.tag == 'figure' and 'fig' in cl:
                figc += 1
                cap = ch.find('figcaption')
                if cap is None:
                    cap = LH.Element('figcaption'); ch.append(cap)
                oc = cap.text_content().strip()
                cap.clear(); cap.text = f'그림 {num}-{figc}. {title}' + (f' — {oc}' if oc else '')
                body.append(LH.tostring(ch, encoding='unicode'))
            elif ch.tag == 'div' and cl == 'gal':
                for f in ch.xpath('.//figure[@class="ph"]'):
                    phc += 1
                    c = f.find('figcaption'); c.text = f'사진 {num}-{phc}. {c.text}'
                body.append(LH.tostring(ch, encoding='unicode'))
            elif ch.tag == 'div' and cl == 'tbwrap':
                tbc += 1
                for tr in ch.xpath('.//tbody/tr'):
                    if (tr.get('class') or '') in ('st', 'sti'):
                        tds = tr.findall('td')
                        if len(tds) >= 2: stars.append(tds[0].text_content().strip() + ': ' + tds[1].text_content().strip())
                body.append(f'<p class="tcap"><b>표 {num}-{tbc}</b> {E(title)}</p>' + LH.tostring(ch, encoding='unicode'))
            elif ch.tag == 'div' and cl == 'board':
                body.append('<div class="codebox"><span class="clabel">암기 코드</span>' + LH.tostring(ch, encoding='unicode') + '</div>')
            elif ch.tag == 'div' and cl == 'kwwrap':
                body.append('<div class="keybox"><div class="khead">핵심 키워드 정리</div>' + LH.tostring(ch, encoding='unicode') + '</div>')
                for tr in ch.xpath('.//tbody/tr'):
                    tds = tr.findall('td')
                    if len(tds) == 2: qa.append((tds[0].text_content().strip(), tds[1].text_content().strip()))
            elif ch.tag == 'p' and 'note' in cl:
                body.append('<div class="callout"><b>참고</b> ' + inner(ch) + '</div>')
            else:
                body.append(LH.tostring(ch, encoding='unicode'))
            if ch.tag == 'ul':
                for li in ch.findall('li'):
                    if 'st' in (li.get('class') or ''): stars.append(li.text_content().strip())
            for st in ch.xpath('.//strong'):
                t = st.text_content().strip()
                if 2 <= len(t) <= 9: terms.append(t)
        # 표 데이터에서도 확인 문제 후보
        if card.find('.//table[@class="tb"]') is not None:
            tb = card.find('.//table[@class="tb"]')
            rows = tb.xpath('.//tbody/tr')
            for tr in rows[:8]:
                tds = tr.findall('td')
                if len(tds) == 2 and len(tds[0].text_content().strip()) <= 14:
                    qa.append(('TB:' + tds[0].text_content().strip() + '|' + title, tds[1].text_content().strip()))
        if not (is_kw or is_ph) and len(objs) < 8 and '사진' not in title and '지도' not in title:
            objs.append(title)
        sid_ = f's{num}-{k}'
        tg = f'<span class="stag">{E(tag)}</span>' if tag else ''
        subs.append(f'<section class="sub{" kwsec" if is_kw else ""}" id="{sid_}"><h3><span class="sn">{num}.{k}</span> {E(title)}{tg}</h3>' + ''.join(body) + '</section>')
    return dict(sid=sid, num=num, label=label, sub=h2 if h2 != label else '', lead=lead, subs=subs, objs=objs, stars=stars, qa=qa, terms=terms, titles=[card_title(c)[0] for c in cards])

chapters = {sid: build_chapter(sid) for sid in chap_no}

def review(ch):
    items = []
    seen = set()
    for q, a in ch['qa']:
        if q.startswith('TB:'):
            who, ttl = q[3:].split('|', 1)
            qq = f'「{ttl}」 표에서 “{who}”의 핵심 내용을 쓰시오.'
        else:
            qq = f'다음 표현이 나오면 무엇(누구)을 떠올려야 하는가? “{q}”'
        if qq in seen: continue
        seen.add(qq); items.append((qq, a))
    # 균등하게 최대 6개
    if len(items) > 6:
        step = len(items) / 6.0
        items = [items[int(i * step)] for i in range(6)]
    return items

# ---------- HTML 조립 ----------
toc, body, contents = '', '', ''
global_terms = {}
for pi, (pn, pt, ids) in enumerate(PARTS):
    toc += f'<li class="tp">{E(pn)} {E(pt)}</li>'
    contents += f'<div class="cpart"><span>{E(pn)}</span> {E(pt)}</div><ol class="clist">'
    body += f'<div class="partpage" id="part{pi+1}"><span>{E(pn)}</span><b>{E(pt)}</b></div>'
    for sid in ids:
        ch = chapters[sid]
        toc += f'<li><a href="#ch{ch["num"]}" data-id="ch{ch["num"]}"><small>제{ch["num"]}장</small>{E(ch["label"])}</a></li>'
        contents += f'<li><a href="#ch{ch["num"]}"><span class="cn">제{ch["num"]}장</span><span class="ct">{E(ch["label"])}</span></a></li>'
        for t in ch['terms']: global_terms.setdefault(t, set()).add(ch['num'])
        obj = ''.join(f'<li>{E(t)}</li>' for t in ch['objs'])
        stars = ''.join(f'<li>{E(s[:105] + ("…" if len(s) > 105 else ""))}</li>' for s in ch['stars'][:6])
        rev = review(ch)
        revh = ''.join(f'<li><details><summary>{E(q)}</summary><p class="ans"><b>답</b> {E(a)}</p></details></li>' for q, a in rev)
        body += (f'<section class="chap" id="ch{ch["num"]}"><header class="chead"><div class="cno">제 {ch["num"]} 장</div><h2>{E(ch["label"])}</h2>'
                 + (f'<p class="csub">{E(ch["sub"])}</p>' if ch['sub'] else '') + '</header>'
                 f'<div class="intro"><p>{E(ch["lead"])}</p></div>'
                 + (f'<div class="goals"><h4>이 장에서 다루는 내용</h4><ul>{obj}</ul></div>' if obj else '')
                 + ''.join(ch['subs'])
                 + (f'<aside class="summary"><h4>핵심 정리 <small>★ 시험에 자주 나오는 표현</small></h4><ul>{stars}</ul></aside>' if stars else '')
                 + (f'<section class="review"><h4>확인 문제</h4><ol>{revh}</ol></section>' if revh else '') + '</section>')
    contents += '</ol>'
# 부록
a = chapters['patterns']
toc += '<li class="tp">부록</li>' + f'<li><a href="#chA" data-id="chA"><small>부록</small>{E(a["label"])}</a></li>'
contents += f'<div class="cpart"><span>부록</span></div><ol class="clist"><li><a href="#chA"><span class="cn">부록 A</span><span class="ct">{E(a["label"])}</span></a></li>'
body += (f'<div class="partpage" id="partA"><span>부록</span><b>기출에서 확인된 패턴</b></div><section class="chap" id="chA"><header class="chead"><div class="cno">부록 A</div><h2>{E(a["label"])}</h2></header>'
         f'<div class="intro"><p>{E(a["lead"])}</p></div>' + ''.join(a['subs']) + '</section>')
for t in a['terms']: global_terms.setdefault(t, set()).add('A')

# 찾아보기
idx = {}
for t, cs in global_terms.items():
    ini = jamo_ini(t[0]) or ('A' if t[0].isalpha() else '#')
    idx.setdefault(ini, []).append((t, sorted(cs, key=lambda x: (str(x) == 'A', int(x) if str(x).isdigit() else 99))))
order = 'ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎA#'
idxh = ''
count = 0
for ini in sorted(idx, key=lambda x: order.index(x) if x in order else 99):
    items = sorted(idx[ini], key=lambda x: x[0])
    idxh += f'<div class="ig"><h5>{E(ini)}</h5><ul>' + ''.join(
        f'<li>{E(t)} <span>' + ', '.join(f'<a href="#ch{c}">{"부록" if c == "A" else str(c) + "장"}</a>' for c in cs) + '</span></li>' for t, cs in items) + '</ul></div>'
    count += len(items)
toc += '<li class="tp">찾아보기</li><li><a href="#index" data-id="index"><small>색인</small>핵심 용어 ' + str(count) + '개</a></li>'
contents += '</ol><div class="cpart"><span>찾아보기</span></div><ol class="clist"><li><a href="#index"><span class="cn">색인</span><span class="ct">핵심 용어 찾아보기</span></a></li></ol>'

body = body.replace('src="img/', 'src="../day01/img/').replace('href="img/', 'href="../day01/img/')
body = fix_ending(body)
credits_el = doc.xpath('//details[@class="credits"]')
credits = LH.tostring(credits_el[0], encoding='unicode').replace('href="img/', 'href="../day01/img/') if credits_el else ''
credits = fix_ending(credits)

# CSS: 원본에서 부품(그림 · 암기 코드 · 흐름도 · 지도 · 사진) 규칙만 가져오기
def seg(a, b): return ORIG_CSS[ORIG_CSS.index(a):ORIG_CSS.index(b)]
parts_css = ''.join([
    seg('.s {', '#prog {'), seg('ul.pts {', '.par {') , seg('.par {', '.note {'), seg('.flow {', '/* 시험 포인트'),
    seg('/* 그림 */', '.hide {'), ORIG_CSS[ORIG_CSS.index('.fig svg.rm {'):ORIG_CSS.index('.gal {')], ORIG_CSS[ORIG_CSS.index('.gal {'):]])

PAGE_CSS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'textbook.css'), encoding='utf-8').read()

page = f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>한국사능력검정시험 심화 교재 · 고대편</title>
<meta name="description" content="한능검 심화 고대사(선사~발해)를 장과 절로 정리한 교재. 학습 내용, 핵심 정리, 확인 문제, 지도와 사진, 찾아보기를 담았어요.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Nanum+Pen+Script&family=Noto+Sans+KR:wght@400;500;700;800&family=Noto+Serif+KR:wght@400;600;700&display=swap">
<style>
{PAGE_CSS}
{parts_css}
</style>
</head>
<body>
<div id="prog" aria-hidden="true"></div>
<button class="menu" id="menu" type="button" aria-label="차례 열기">☰ 차례</button>
<div class="layout">
<aside class="toc" id="toc" aria-label="차례">
  <p class="brand">한국사능력검정시험<br>심화 교재</p>
  <p class="meta">고대편 · 선사 시대 ~ 발해</p>
  <ol>{toc}</ol>
  <button class="focusbtn" id="focus" type="button" aria-pressed="false">★ 핵심 문장만 진하게</button>
  <p class="back"><a href="../">← 전체 목록</a> · <a href="../day01/">강의 노트 버전</a></p>
</aside>
<div class="book">
<header class="cover">
  <p class="ed">한국사능력검정시험 · 심화</p>
  <h1>한능검 핵심 교재<small>고대편 · 선사 시대부터 발해까지</small></h1>
  <p class="by">서경석의 다이어트 한능검 강의를 바탕으로 장 · 절 체계로 다시 엮음</p>
</header>
<nav class="contents" id="contents" aria-label="차례">
  <h2>차 례</h2>
  {contents}
</nav>
<section class="howto" aria-label="이 책의 구성">
  <h2>이 책의 구성</h2>
  <dl>
    <dt>이 장에서 다루는 내용</dt><dd>장의 첫머리에서 무엇을 배우는지 먼저 보여 준다.</dd>
    <dt><em class="s"></em> 별 표시</dt><dd>시험에 자주 나온다고 강조된 표현이다. 장 끝의 “핵심 정리”에 다시 모았다.</dd>
    <dt>암기 코드</dt><dd>순서와 이름을 한 번에 외우도록 만든 앞글자 코드다. 파란 타일의 글자를 이어 읽는다.</dd>
    <dt>핵심 키워드 정리</dt><dd>“이 표현이 나오면 이것”이라는 짝을 표로 묶었다.</dd>
    <dt>확인 문제</dt><dd>장 끝에서 스스로 점검한다. 문제를 누르면 답이 펼쳐진다.</dd>
    <dt>그림 · 사진</dt><dd>지도는 실제 해안선 위에 그린 약도이고, 사진은 Wikimedia Commons의 자유 이용 이미지다. 출처는 책 끝에 있다.</dd>
  </dl>
</section>
<main>
{body}
<section class="chap" id="index"><header class="chead"><div class="cno">찾아보기</div><h2>핵심 용어 찾아보기</h2></header><div class="idx">{idxh}</div></section>
</main>
{credits}
<footer>이 교재는 유튜브 자동 자막을 바탕으로 정리했다. 고유명사는 문맥으로 보정했으므로 시험 전에는 정식 교재와 한 번 더 대조하기 바란다.</footer>
</div>
</div>
<script>
(function () {{
  var prog = document.getElementById('prog'), links = [].slice.call(document.querySelectorAll('.toc a')), chaps = [].slice.call(document.querySelectorAll('section.chap'));
  function onScroll() {{
    var h = document.documentElement.scrollHeight - innerHeight;
    prog.style.width = (h > 0 ? Math.min(100, scrollY / h * 100) : 0) + '%';
    var cur = null; chaps.forEach(function (s) {{ if (s.getBoundingClientRect().top < innerHeight * 0.4) cur = s.id; }});
    links.forEach(function (a) {{ a.classList.toggle('on', a.getAttribute('data-id') === cur); }});
  }}
  addEventListener('scroll', onScroll, {{ passive: true }}); onScroll();
  var menu = document.getElementById('menu');
  menu.addEventListener('click', function () {{ document.body.classList.toggle('toc-open'); }});
  links.forEach(function (a) {{ a.addEventListener('click', function () {{ document.body.classList.remove('toc-open'); }}); }});
  var fb = document.getElementById('focus');
  fb.addEventListener('click', function () {{ var on = document.body.classList.toggle('focus'); fb.setAttribute('aria-pressed', on ? 'true' : 'false'); }});
}})();
</script>
</body>
</html>
'''
os.makedirs(os.path.dirname(OUT), exist_ok=True)
io.open(OUT, 'w', encoding='utf-8', newline='\n').write(page)
left = len(re.findall(r'[가-힣]요(?=[.)”"’]*(?:</|\s))', re.sub(r'<[^>]+>', '', body)))
print('built', len(page), 'chars; chapters', len(chapters), '; index terms', count, '; leftover 요 endings', left)
