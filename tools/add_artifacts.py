# -*- coding: utf-8 -*-
"""강의(Day-01~03)에 나온 문화유산 사진과 특징을 한곳에 모은 섹션(#artifacts)을 만들어요. 여러 번 실행해도 결과가 같아요.
실행 순서: add_day03.py → add_photos2.py → add_artifacts.py"""
import io, os, re, json, urllib.parse
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'day01', 'index.html')
IMG = os.path.join(ROOT, 'day01', 'img')
META = {m['k']: m for m in json.load(io.open(os.path.join(ROOT, 'tools', 'photos2_meta.json'), encoding='utf-8'))}
STAR = '<em class="s" aria-label="중요"></em>'


def fx(t):
    t = t.replace('★', STAR)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'\(\((.+?)\)\)', r'<span class="par">(\1)</span>', t)
    return t


# 강의에 나오지 않은 사진은 뺀다 (다뉴세문경 계열 거울, 완도 장도)
s = io.open(P, encoding='utf-8').read()
for k in ('jeongmun', 'jangdo'):
    s = re.sub(r'<figure class="ph"><a href="img/%s\.jpg".*?</figure>' % k, '', s, flags=re.S)
    f = os.path.join(IMG, k + '.jpg')
    if os.path.exists(f):
        os.remove(f)
for key in ('Jeongmun', '%EC%A0%95%EB%AC%B8%EA%B2%BD', 'Jangdo_bridge'):
    s = re.sub(r'<li><b>[^<]*</b> — [^<]*<a href="https://commons\.wikimedia\.org/wiki/File:[^"]*%s[^"]*"[^>]*>[^<]*</a></li>' % re.escape(key), '', s)
# 빈 갤러리 카드 정리
s = re.sub(r'<article class="card figc"><h3>관련 유물·유적 사진</h3><div class="gal"></div></article>', '', s)

# (키, 이름, 시대·나라, 특징들) — ★는 강사가 직접 강조한 항목
G = []
G.append(('불상', '불상은 얼굴·광배·몇 존인지를 보고 나라를 맞히는 문제가 나와요', [
 ('banga', '금동미륵보살 반가사유상', '삼국 시대', [
   '★“아주 중요, 별 다섯 개를 쳐도 모자랄 정도”라고 했어요. 한쪽 다리를 올리고 앉아 **생각에 잠긴(반가사유)** 모습이에요.',
   '고구려·백제·신라 **삼국 모두**에 있어요. 일본 **고류사의 목조 미륵보살 반가사유상**과 거의 똑같아서 **삼국의 불상 문화가 일본에 영향**을 줬다는 증거예요.']),
 ('yeonga7', '금동 연가 7년명 여래 입상', '고구려', [
   '금동으로 만들었고 **광배 뒷면**에 당시 연호인 **“연가 7년”**이 새겨져 있어서 이런 이름이 붙었어요.',
   '뒤에 **광배(빛나는 후광)**가 있다는 점이 핵심이에요. 이 영향을 받은 것이 발해의 이불병좌상이에요.']),
 ('seosan', '서산 용현리 마애여래삼존상', '백제', [
   '★“정말 중요”하다고 했어요. 서산 용현리의 **벼랑(바위 언덕)을 갈아서** 새긴 **마애불**이고, 가운데 여래상과 양옆 보살상, **세 분(삼존)**이에요.',
   '★얼굴 표정이 **“백제의 미소”**예요. 반드시 기억하라고 했어요.']),
 ('baedong', '경주 배동 석조여래삼존입상', '신라', [
   '돌로 만든 여래상 **세 분**이 서 있는 모습이에요. 자주 나오지 않고 주로 오답 선지로 나오니 **“신라 시대”**라는 것만 기억해요.']),
 ('ibul', '이불병좌상', '발해', [
   '**두 부처가 나란히 앉은(병좌)** 모습이고 뒤에 **광배**가 있어요.',
   '고구려 **연가 7년명 금동여래입상**의 광배 양식에 영향을 받았어요. 발해가 **고구려 문화를 이었다**는 증거예요.']),
 ('seokguram', '석굴암 본존불', '통일신라', [
   '통일신라를 대표하는 본존불이에요. **둥근 천장**과 벽의 **정교한 조각**이 특징이고, 김대성이 불국사와 함께 만들었다고 했어요.']),
]))
G.append(('탑·석등·승탑', '탑은 층수·모양·이름의 유래를 짝지어 외워요', [
 ('jeongnimsa', '부여 정림사지 5층 석탑', '백제(사비 시대)', [
   '★“너무 중요”하다고 했어요. **5층 석탑**이고 **부여**에 있어요((공주가 아니에요)).',
   '660년 **당의 소정방**이 “백제를 평정했다”고 새겨 놓아 **평제탑**이라고도 불러요.']),
 ('mireuksa', '익산 미륵사지 석탑', '백제(무왕)', [
   '★“너무 중요”하다고 했어요. **무왕**이 세웠어요. 코드는 **“무미건조, 무익(익산)”**이에요.',
   '현존하는 **가장 오래된, 가장 큰 석탑**이에요. 탑 안에서 **금제 사리봉영기**가 나왔고, 거기 적힌 **사택씨 딸**과 무왕의 관계 때문에 연구자들이 혼란을 겪었어요. ((사택지적비의 사택지적과 구분))',
   '오답 선지로 **익산 왕국리 5층 석탑**이 나와요. 시기는 모르지만 **지역이 익산**인 것만 알아요.']),
 ('bunhwangsa', '분황사 모전석탑', '신라(선덕여왕)', [
   '**신라에서 가장 오래된 석탑**이에요. **벽돌탑(전탑)을 모방한(모전) 돌탑**이에요.',
   '선덕여왕 코드 **“황분첨”**: **황**룡사 9층 목탑 · **분**황사 모전석탑 · **첨**성대. 황룡사 목탑은 **자장**의 건의로 만들었고 절은 진흥왕 때 세웠어요.']),
 ('dabotap', '불국사 다보탑', '통일신라', [
   '**계단**이 있고 **10원짜리 동전**의 모델이에요. 석가탑과 마주 보고 있어요.']),
 ('seokgatap', '불국사 3층 석탑(석가탑 · 무영탑)', '통일신라', [
   '석가탑 = 불국사 3층 석탑 = **무영탑(그림자 없는 탑)**, 이름을 모두 알아야 해요. 아사달·아사녀 전설에서 연못에 그림자가 비치지 않았다는 데서 나온 이름이에요.',
   '★탑을 보수하다가 **무구정광대다라니경**이 나왔어요. **현존 가장 오래된 목판 인쇄물**이에요. ((가장 오래된 금속활자본은 고려의 직지심체요절))']),
 ('gameunsa', '감은사지 3층 석탑', '통일신라(신문왕)', [
   '**문무왕**을 위해 시작해 아들 **신문왕** 때 완성했어요. **아버지 은혜에 감사한다**는 뜻이라 꼭대기가 **하늘까지 닿을 듯 뾰족**해요.',
   '통일신라 석탑은 대부분 **3층**이에요. ((고려로 넘어가면 다각·다층))']),
 ('hwaeomsa', '화엄사 4사자 3층 석탑', '통일신라', [
   '**사자 네 마리**가 탑을 받치고 있는 3층 석탑이에요. 전남에 있어요.']),
 ('stupa', '화순 쌍봉사 철감선사탑', '통일신라 말', [
   '스님의 사리를 보관하는 **승탑**이에요. 통일신라 말 **선종이 유행**했음을 보여 줘요. ((교종 대신 참선을 중시, 선문 중 **가지산문**의 대표는 체징))',
   '**둥글둥글하고 부피감**이 있어요. 발해 석등은 날씬하고 쭉 뻗어서 사진 문제에서 구분해요.']),
 ('seokdeung', '발해 석등', '발해', [
   '승탑에 비해 **날씬하고 길게 뻗은** 모양이에요. 사진에서 승탑과 구분하는 포인트예요.']),
 (None, '영광탑', '발해', [
   '발해의 **유일한 탑**이고 **벽돌탑(전탑)**이에요. **아래의 아치형 입구**로 알아봐요. ((자유 이용 사진을 찾지 못해 사진은 없어요))']),
]))
G.append(('무덤과 유물', '무덤은 어느 나라의 어떤 양식인지 연결해서 외워요', [
 ('hou', '호우명 그릇', '고구려·신라', [
   '그릇 바닥에 **“광개토지호태왕”** 글자가 있어요. **신라 땅의 호우총**에서 나와 **고구려와 신라의 교류**를 보여 줘요.']),
 ('muryeong', '무령왕릉(공주 송산리)', '백제', [
   '★**벽돌무덤**이고 중국 **남조 양나라**의 영향을 받았어요. **삼국 시대 무덤 중 유일하게 주인(무령왕)과 만든 연대를 정확히 아는** 무덤이에요.',
   '**매지권**은 땅을 샀다는 증서로 **도교의 영향**이에요. 무령왕은 22담로에 왕족을 파견한 왕이에요.']),
 ('seoksu', '무령왕릉 석수(진묘수)', '백제', [
   '★“아주 중요”하다고 했어요. 돌로 만든 동물상으로 무덤을 지키는 역할을 해요.']),
 ('incense', '백제 금동대향로', '백제(사비)', [
   '몸체는 **용**이 받치고 **연꽃잎(불교)**이 있고, 꼭대기에 **봉황**과 **신선·악사 5명(도교)**이 있어요. **불교와 도교**가 함께 들어 있어요.',
   '**부여 능산리**에서 나왔어요. 공주는 송산리 고분군이에요. **“부능공송”**으로 외워요.']),
 ('chiljido', '칠지도', '백제', [
   '가지가 **일곱 개**인 칼이에요. **일본의 국보**로 있고, **백제와 왜가 교류**했음을 보여 줘요.']),
 ('gima', '기마인물형 토기', '신라', [
   '말을 탄 사람 모양의 토기예요. **신라의 것**이라는 점만 알면 돼요.']),
 ('daegaya', '대가야 금동관', '대가야', [
   '대가야 옛 땅 **고령 지산동**에서 나온 금동관이에요. 코드: 고령 **지산동** = **“학수 고대”** = 대가야.']),
 ('cheonmado', '천마도(천마총)', '신라', [
   '말 **안장 가리개(장니)**에 그려진 **하늘을 나는 말** 그림이에요. **벽화가 아니에요.** 신라 무덤은 돌무지덧널무덤이라 **벽화가 거의 없어요.**',
   '**총**은 주인을 모르는 무덤, **능**은 아는 무덤이에요. 천마도가 나와 천마총, 금관이 나와 금관총이라 불러요.']),
 ('crown', '신라 금관', '신라', [
   '금관총·황남대총·천마총 같은 신라 **돌무지덧널무덤**에서 나왔어요. 도굴이 안 돼서 **껴묻거리**가 많이 남았어요.']),
 ('hwangnam', '경주 황남대총', '신라', [
   '신라 **돌무지덧널무덤**이에요. 입구가 없어 도굴이 안 돼 **껴묻거리**가 많아요.']),
 ('janggunchong', '장군총', '고구려', [
   '**돌무지무덤**의 대표예요. 고구려 초기에 많았어요.']),
 ('seokchon', '서울 석촌동 고분군', '백제 초기', [
   '고구려의 영향으로 **돌무지무덤** 형태가 보여요.']),
 ('gangseo', '강서대묘(현무)', '고구려', [
   '평양의 **굴식 돌방무덤**이에요. **모줄임 천장**이 특징이고, 입구가 있어서 **도굴이 쉬웠어요.** 벽에 **사신도(청룡·백호·주작·현무)**가 있어요 ((도교의 영향)).']),
 ('jeonghye', '정혜공주묘', '발해', [
   '문왕의 **둘째 딸**의 무덤이에요. **굴식 돌방무덤**, **모줄임 천장**으로 **고구려의 영향**을 보여 줘요.']),
 ('lion_balhae', '발해 돌사자(정혜공주묘 계통)', '발해', [
   '정혜공주묘에서 나온 **돌사자상**은 고구려 사자상과 비슷해요. **고구려 영향**의 증거예요.']),
 ('jeonghyo', '정효공주묘 벽화', '발해', [
   '문왕의 **넷째 딸**의 무덤이에요. **벽돌무덤**이라 **당의 영향**이고, 천장은 고구려식이라 **두 문화의 영향**이 모두 있어요.']),
 ('daeseongdong', '김해 대성동 고분군', '금관가야', [
   '유네스코 세계유산이에요. 김대성 → **“김해 대성동 = 금관가야”**로 외워요. 금관가야는 **법흥왕**이 멸망시켰어요 (“범금법금”).']),
 ('jisandong', '고령 지산동 고분군', '대가야', [
   '유네스코 세계유산이에요. **“고령 지산동 = 대가야(학수 고대)”**이고 **진흥왕**이 멸망시켰어요 (“진대”).']),
 ('gaya_armor', '가야 철제 갑옷', '가야', [
   '가야가 **철**로 유명했음을 보여 줘요. 사진만 보고 가야 것으로 맞히는 문제가 나와요.']),
]))
G.append(('비석·문서·기타', '비석은 새겨진 내용과 지역을 같이 알아요', [
 ('stele', '광개토대왕릉비', '고구려', ['**연호 “영락”**이 쓰여 있어요. 우리 역사 **최초의 연호**예요.']),
 ('jungseong', '포항 중성리 신라비', '신라', ['포항에서 발견된 신라 비석으로 문제 **선지**로 나온 적이 있어요.']),
 ('sataek', '사택지적비', '백제', ['백제 귀족 **사택지적**이 늙어 가는 무상함에 **불교에 귀의**하려 한 내용이에요. 유교·불교·도교가 모두 보인다고 했어요. ((미륵사지 사리봉영기의 사택씨와 비교))']),
 ('hyecho', '왕오천축국전', '통일신라', ['**혜초**가 인도와 중앙아시아 다섯 나라를 여행하고 쓴 책이에요. **“혜초 왕오천축국전”**으로 외워요.']),
 ('daewangam', '문무대왕릉(대왕암)', '통일신라', ['**수중릉**이에요. 문무왕이 “죽어서 동해의 용이 되어 왜의 침략을 막겠다”고 유언했어요. 만든 것은 아들 **신문왕**이에요.']),
 ('jikji', '직지심체요절', '고려', ['현존하는 **가장 오래된 금속활자본**이에요. ((가장 오래된 목판 인쇄물은 무구정광대다라니경))']),
]))

# ── 크레딧용 정보: 새 사진(photos2_meta)만 출처를 더한다. 기존 사진은 이미 등록돼 있다.
def dim(k):
    f = os.path.join(IMG, k + '.jpg')
    with Image.open(f) as im:
        return im.size


html = '<section class="sec" id="artifacts"><header class="sh"><span class="era">Day-02 · 사진 학습</span><h2>사진으로 나오는 문화유산과 그 특징</h2><p class="lead">강사가 “1점 같지 않은 1점 문제”라며 사진으로 집중 학습한 유물만 모았어요. 강의에 나오지 않은 유물은 넣지 않았어요. 별은 강사가 특히 강조한 특징이에요.</p></header>'
used = []
for title, lead, items in G:
    body = ''
    for k, name, era, feats in items:
        if k:
            if not os.path.exists(os.path.join(IMG, k + '.jpg')):
                print('사진 없음:', k); continue
            w, h = dim(k)
            used.append((k, name))
            ph = '<a class="aph" href="img/%s.jpg" target="_blank" rel="noopener"><img src="img/%s.jpg" alt="%s" loading="lazy" width="%d" height="%d"></a>' % (k, k, name, w, h)
        else:
            ph = '<div class="aph nop">사진 없음</div>'
        lis = ''.join('<li class="%s">%s</li>' % ('st' if f.startswith('★') else '', fx(f)) for f in feats)
        body += '<div class="art">%s<div class="abody"><h4>%s<span class="par">(%s)</span></h4><ul class="pts">%s</ul></div></div>' % (ph, name, era, lis)
    html += '<article class="card figc"><h3>%s</h3><p class="note">%s</p>%s</article>' % (title, lead, body)
html += '</section>\n'

CSS = '''/* 문화유산 사진 학습 */
.art { display: grid; grid-template-columns: 150px minmax(0, 1fr); gap: 14px; padding: 12px 0; border-top: 1px dotted var(--line); }
.art:first-of-type { border-top: 0; }
.art .aph { display: block; align-self: start; border-radius: 8px; overflow: hidden; background: var(--sheet); }
.art .aph img { display: block; width: 100%; height: 150px; object-fit: cover; }
.art .nop { display: grid; place-items: center; height: 150px; font-size: 13px; color: var(--muted); }
.art h4 { margin: 0 0 4px; font: 800 16px/1.4 var(--f-body); }
.art h4 .par { margin-left: 6px; font-weight: 500; }
@media (max-width: 520px) { .art { grid-template-columns: 96px minmax(0, 1fr); gap: 10px; } .art .aph img, .art .nop { height: 96px; } }
'''
MARK = '/* 문화유산 사진 학습 */'
if MARK in s:
    s = re.sub(re.escape(MARK) + r'.*?(?=/\* [^*]+\*/|</style>)', CSS, s, count=1, flags=re.S)
else:
    s = s.replace('</style>', CSS + '</style>', 1)

a = s.find('<section class="sec" id="artifacts"')
if a >= 0:
    e = s.index('</section>', a) + len('</section>\n')
    s = s[:a] + s[e:]
band = s.index('<div class="dayhead" id="day3">')
s = s[:band] + html + s[band:]

# 출처: 새로 쓴 사진 가운데 목록에 없는 것만 추가
for k, name in used:
    m = META.get(k)
    if not m:
        continue
    q = urllib.parse.quote(m['title'].replace(' ', '_'), safe=':()_.-,')
    if q in s:
        continue
    artist = re.sub(r'(Unknown author)+', '작자 미상', m['artist']) or '작자 미상'
    li = '<li><b>%s</b> — %s · %s · <a href="https://commons.wikimedia.org/wiki/%s" target="_blank" rel="noopener">원본(Wikimedia Commons)</a></li>' % (name, artist, m['lic'], q)
    s = s.replace('</ol></details><footer>', li + '</ol></details><footer>', 1)
n = len(set(re.findall(r'<img src="img/([^"]+)"', s)))
s = re.sub(r'사진 · 지도 출처 \(\d+장\)', '사진 · 지도 출처 (%d장)' % n, s, count=1)
io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('고유 사진', n, '장, 문화유산 섹션 항목', sum(len(i[2]) for i in G))
