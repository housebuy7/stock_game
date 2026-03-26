import random
from datetime import datetime, timedelta
import json

# 환율 설정 (상수)
USD_RATE = 1430.0

# ============================================================
# 1. 뉴스 & 이벤트 시스템
# ============================================================
TIMELINE_NEWS = [
    {"date": "2021-10-15", "type": "precursor", "sector": "Crypto", "title": "고래 지갑 대량 이동 포착",
     "content": "상위 100개 지갑에서 거래소로 대규모 BTC 이체가 감지되었습니다.",
     "price": 200000, "reliability": 0.8, "fake": False, "requires_premium": False,
     "sector_effects": {"Crypto": -0.3}},
    {"date": "2021-11-08", "type": "main", "sector": "Crypto", "title": "비트코인 역사적 고점 $69K 돌파",
     "content": "비트코인이 사상 최고가를 경신했지만 고래 매도세가 강해지고 있습니다.",
     "price": 1000000, "reliability": 1.0, "fake": False, "requires_premium": False,
     "sector_effects": {"Crypto": -0.5}},
    {"date": "2021-11-20", "type": "aftermath", "sector": "Crypto", "title": "코인 시장 조정 시작",
     "content": "비트코인 10% 이상 하락. 알트코인 시장 연쇄 청산 발생.",
     "price": 0, "reliability": 1.0, "fake": False, "requires_premium": False,
     "sector_effects": {"Crypto": -0.4}},
    {"date": "2022-01-20", "type": "precursor", "sector": "Default", "title": "동유럽 긴장 고조",
     "content": "러시아군 국경 집결 위성사진 확인. NATO 긴급회의 소집.",
     "price": 300000, "reliability": 0.7, "fake": False, "requires_premium": False,
     "sector_effects": {"Default": -0.2, "Auto": -0.1}},
    {"date": "2022-02-24", "type": "main", "sector": "Default", "title": "러시아, 우크라이나 침공 개시",
     "content": "전면전 돌입. 원유·천연가스 가격 급등, 글로벌 증시 급락.",
     "price": 0, "reliability": 1.0, "fake": False, "requires_premium": False,
     "sector_effects": {"Default": -0.6, "Semiconductor": -0.3, "Auto": -0.4}},
    {"date": "2022-04-25", "type": "precursor", "sector": "Crypto", "title": "[내부자] 알고리즘 스테이블 취약점 발견",
     "content": "특정 알고리즘 스테이블코인에서 디페깅 시뮬레이션이 성공했다는 보고.",
     "price": 3000000, "reliability": 0.9, "fake": False, "requires_premium": True,
     "sector_effects": {"Crypto": -0.8}},
    {"date": "2022-05-07", "type": "main", "sector": "Crypto", "title": "루나/테라 붕괴 시작",
     "content": "UST 디페깅 발생. LUNA 가격 99% 폭락. 시장 패닉.",
     "price": 0, "reliability": 1.0, "fake": False, "requires_premium": False,
     "sector_effects": {"Crypto": -0.9}},
    {"date": "2022-04-10", "type": "precursor", "sector": "Default", "title": "연준 매파 발언 증가",
     "content": "다수의 연준 위원들이 0.50%p 인상(빅스텝) 가능성을 시사.",
     "price": 500000, "reliability": 0.8, "fake": False, "requires_premium": False,
     "sector_effects": {"Default": -0.3, "Semiconductor": -0.2, "Crypto": -0.4}},
    {"date": "2022-05-05", "type": "main", "sector": "Default", "title": "연준, 0.50%p 금리 인상 단행",
     "content": "자이언트 스텝 현실화. 기술주·코인 동반 급락.",
     "price": 0, "reliability": 1.0, "fake": False, "requires_premium": False,
     "sector_effects": {"Default": -0.3, "Semiconductor": -0.4, "Crypto": -0.5}},
    {"date": "2022-10-28", "type": "precursor", "sector": "Crypto", "title": "[찌라시] FTX 자금 유용 의혹",
     "content": "익명 트레이더가 FTX의 재무 건전성에 의문을 제기했습니다.",
     "price": 100000, "reliability": 0.3, "fake": False, "requires_premium": False,
     "sector_effects": {"Crypto": -0.2}},
    {"date": "2022-11-02", "type": "main", "sector": "Crypto", "title": "FTX 유동성 위기 공식 확인",
     "content": "세계 3위 거래소 FTX, 인출 중단. 바이낸스 인수 협상 후 결렬.",
     "price": 0, "reliability": 1.0, "fake": False, "requires_premium": False,
     "sector_effects": {"Crypto": -0.7}},
    {"date": "2022-11-15", "type": "precursor", "sector": "Auto", "title": "중국 전기차 보조금 축소 예정",
     "content": "중국 정부의 전기차 보조금 종료 임박. 수요 급감 우려.",
     "price": 500000, "reliability": 0.7, "fake": False, "requires_premium": False,
     "sector_effects": {"Auto": -0.4}},
    {"date": "2022-12-20", "type": "main", "sector": "Auto", "title": "테슬라 주가 $100 붕괴",
     "content": "경기침체 + 수요 둔화 + CEO 리스크 삼중고.",
     "price": 0, "reliability": 1.0, "fake": False, "requires_premium": False,
     "sector_effects": {"Auto": -0.5}},
    {"date": "2023-01-10", "type": "precursor", "sector": "Semiconductor", "title": "생성형 AI 서비스 폭발적 성장",
     "content": "챗GPT 사용자 1억명 돌파. GPU 수요 급증 예상.",
     "price": 1000000, "reliability": 0.8, "fake": False, "requires_premium": False,
     "sector_effects": {"Semiconductor": 0.6}},
    {"date": "2023-01-25", "type": "main", "sector": "Semiconductor", "title": "엔비디아, AI 칩 주문 폭주",
     "content": "데이터센터용 GPU 공급 부족 심화. H100 칩 6개월 대기.",
     "price": 0, "reliability": 1.0, "fake": False, "requires_premium": False,
     "sector_effects": {"Semiconductor": 0.7}},
    {"date": "2023-05-10", "type": "precursor", "sector": "Semiconductor", "title": "[내부자] 엔비디아 실적 역대급 예상",
     "content": "데이터센터 매출 전년비 300% 증가 추정. 갭상승 대비.",
     "price": 5000000, "reliability": 0.95, "fake": False, "requires_premium": True,
     "sector_effects": {"Semiconductor": 0.8}},
    {"date": "2023-05-24", "type": "main", "sector": "Semiconductor", "title": "엔비디아 실적 서프라이즈 발표",
     "content": "시장 예상치 2배 초과 달성. 시간외 20% 급등.",
     "price": 0, "reliability": 1.0, "fake": False, "requires_premium": False,
     "sector_effects": {"Semiconductor": 0.9}},
    {"date": "2023-07-15", "type": "precursor", "sector": "Bio", "title": "신종 감염병 우려 재부상",
     "content": "WHO, 새로운 변이 바이러스 모니터링 강화 권고.",
     "price": 300000, "reliability": 0.5, "fake": False, "requires_premium": False,
     "sector_effects": {"Bio": 0.4, "Auto": -0.1}},
    {"date": "2023-08-01", "type": "main", "sector": "Bio", "title": "글로벌 제약사 백신 개발 경쟁 재점화",
     "content": "각국 정부 긴급 방역 예산 편성. 바이오주 동반 상승.",
     "price": 0, "reliability": 1.0, "fake": False, "requires_premium": False,
     "sector_effects": {"Bio": 0.6, "Auto": -0.2}},
    {"date": "2023-12-15", "type": "precursor", "sector": "Crypto", "title": "SEC 비트코인 ETF 승인 임박설",
     "content": "다수의 자산운용사가 SEC와 최종 협의 단계에 진입.",
     "price": 2000000, "reliability": 0.8, "fake": False, "requires_premium": False,
     "sector_effects": {"Crypto": 0.5}},
    {"date": "2024-01-10", "type": "main", "sector": "Crypto", "title": "비트코인 현물 ETF 공식 승인",
     "content": "SEC, 11개 비트코인 현물 ETF 동시 승인. 기관 자금 유입 시작.",
     "price": 0, "reliability": 1.0, "fake": False, "requires_premium": False,
     "sector_effects": {"Crypto": 0.7}},
    {"date": "2024-06-01", "type": "precursor", "sector": "Semiconductor", "title": "[찌라시] AI 투자 거품 경고",
     "content": "월가 일부 애널리스트, AI 관련주 밸류에이션 과열 지적.",
     "price": 200000, "reliability": 0.4, "fake": False, "requires_premium": False,
     "sector_effects": {"Semiconductor": -0.2}},
    {"date": "2024-07-15", "type": "main", "sector": "Semiconductor", "title": "AI주 일시 조정, 차익실현 매물 출회",
     "content": "엔비디아 등 AI 대장주 10~15% 조정. 건전한 조정 vs 꼭지 논란.",
     "price": 0, "reliability": 1.0, "fake": False, "requires_premium": False,
     "sector_effects": {"Semiconductor": -0.3}},
    {"date": "2021-12-01", "type": "precursor", "sector": "Auto", "title": "[찌라시] 테슬라 비밀 배터리 기술 유출",
     "content": "테슬라가 혁신적 고체전지 양산에 성공했다는 미확인 정보.",
     "price": 150000, "reliability": 0.1, "fake": True, "requires_premium": False,
     "sector_effects": {"Auto": 0.3}},
    {"date": "2022-08-15", "type": "precursor", "sector": "Semiconductor", "title": "[찌라시] 삼성전자 엔비디아 인수 협상",
     "content": "삼성전자가 엔비디아 지분 인수를 논의 중이라는 루머.",
     "price": 100000, "reliability": 0.05, "fake": True, "requires_premium": False,
     "sector_effects": {"Semiconductor": 0.4}},
    {"date": "2023-03-01", "type": "precursor", "sector": "Crypto", "title": "[찌라시] 중국 비트코인 합법화 검토",
     "content": "중국 정부가 비트코인 거래를 재허용할 것이라는 소문.",
     "price": 80000, "reliability": 0.05, "fake": True, "requires_premium": False,
     "sector_effects": {"Crypto": 0.5}},
    {"date": "2023-09-15", "type": "precursor", "sector": "Bio", "title": "[찌라시] 삼성바이오 글로벌 M&A 추진",
     "content": "삼성바이오가 미국 대형 제약사 인수를 추진한다는 소문.",
     "price": 120000, "reliability": 0.1, "fake": True, "requires_premium": False,
     "sector_effects": {"Bio": 0.3}},
    {"date": "2024-03-01", "type": "precursor", "sector": "Default", "title": "[찌라시] 애플 자율주행차 출시 임박",
     "content": "애플이 2024년 내 자율주행 전기차를 공개한다는 미확인 정보.",
     "price": 100000, "reliability": 0.08, "fake": True, "requires_premium": False,
     "sector_effects": {"Default": 0.2, "Auto": 0.1}},
]

# ============================================================
# 2. 플레이어 스킬 트리
# ============================================================
SKILL_TREE = {
    "info_basic": {
        "name": "기초 정보력", "desc": "무료 뉴스 속보 자동 수신",
        "cost": 500000, "category": "info", "level": 1, "prereq": None,
        "effect": {"news_speed": 1}
    },
    "info_advanced": {
        "name": "고급 애널리스트", "desc": "뉴스 신뢰도 표시 + 찌라시 감별 확률 50%",
        "cost": 2000000, "category": "info", "level": 2, "prereq": "info_basic",
        "effect": {"fake_detect": 0.5}
    },
    "info_insider": {
        "name": "내부자 네트워크", "desc": "내부자 정보 열람 가능 + 찌라시 감별 90%",
        "cost": 10000000, "category": "info", "level": 3, "prereq": "info_advanced",
        "effect": {"premium_access": True, "fake_detect": 0.9}
    },
    "trade_basic": {
        "name": "수수료 할인", "desc": "거래 수수료 50% 할인",
        "cost": 300000, "category": "trade", "level": 1, "prereq": None,
        "effect": {"fee_discount": 0.5}
    },
    "trade_leverage": {
        "name": "신용거래 해금", "desc": "2배 레버리지 사용 가능",
        "cost": 3000000, "category": "trade", "level": 2, "prereq": "trade_basic",
        "effect": {"leverage": 2.0}
    },
    "trade_short": {
        "name": "공매도 해금", "desc": "하락에도 수익! 공매도 거래 가능",
        "cost": 8000000, "category": "trade", "level": 3, "prereq": "trade_leverage",
        "effect": {"short_sell": True}
    },
    "algo_basic": {
        "name": "자동 손절", "desc": "-5% 자동 손절 봇 활성화",
        "cost": 5000000, "category": "algo", "level": 1, "prereq": "trade_basic",
        "effect": {"auto_stoploss": -5.0}
    },
    "algo_advanced": {
        "name": "맞춤 알고리즘", "desc": "손절/익절 % 직접 설정 가능",
        "cost": 15000000, "category": "algo", "level": 2, "prereq": "algo_basic",
        "effect": {"custom_algo": True}
    },
    "algo_ai": {
        "name": "AI 트레이딩 봇", "desc": "AI가 자동으로 최적 매매 (수익의 10% 수수료)",
        "cost": 50000000, "category": "algo", "level": 3, "prereq": "algo_advanced",
        "effect": {"ai_bot": True}
    },
}

# ============================================================
# 3. 부동산 & 수집품 시스템
# ============================================================
PROPERTIES = {
    "gosiwon": {
        "name": "고시원", "desc": "좁지만 싸다. 생존의 시작.",
        "cost": 0, "monthly_cost": 300000,
        "buffs": {"stress_recovery": 1, "info_bonus": 0.0},
        "tier": 0,
    },
    "oneroom": {
        "name": "원룸", "desc": "나만의 공간. 작지만 소중해.",
        "cost": 50000000, "monthly_cost": 500000,
        "buffs": {"stress_recovery": 2, "info_bonus": 0.05},
        "tier": 1,
    },
    "apt_small": {
        "name": "소형 아파트", "desc": "서울 외곽 25평. 드디어 안정감.",
        "cost": 300000000, "monthly_cost": 800000,
        "buffs": {"stress_recovery": 3, "info_bonus": 0.10},
        "tier": 2,
    },
    "apt_large": {
        "name": "강남 아파트", "desc": "강남 40평대. 상류층 진입.",
        "cost": 1500000000, "monthly_cost": 1500000,
        "buffs": {"stress_recovery": 5, "info_bonus": 0.20},
        "tier": 3,
    },
    "penthouse": {
        "name": "한강뷰 펜트하우스", "desc": "한강이 보이는 최상층. 부의 상징.",
        "cost": 5000000000, "monthly_cost": 3000000,
        "buffs": {"stress_recovery": 8, "info_bonus": 0.30},
        "tier": 4,
    },
    "mansion": {
        "name": "대저택", "desc": "프라이빗 정원과 수영장. 재벌의 삶.",
        "cost": 20000000000, "monthly_cost": 10000000,
        "buffs": {"stress_recovery": 10, "info_bonus": 0.50},
        "tier": 5,
    },
}

COLLECTIBLES = [
    {"id": "watch_1", "name": "롤렉스 서브마리너", "cost": 15000000, "category": "시계", "tier": 1},
    {"id": "watch_2", "name": "파텍필립 노틸러스", "cost": 80000000, "category": "시계", "tier": 2},
    {"id": "watch_3", "name": "리샤르밀 RM 011", "cost": 500000000, "category": "시계", "tier": 3},
    {"id": "car_1", "name": "BMW M4", "cost": 120000000, "category": "자동차", "tier": 1},
    {"id": "car_2", "name": "포르쉐 911 터보S", "cost": 350000000, "category": "자동차", "tier": 2},
    {"id": "car_3", "name": "람보르기니 우라칸", "cost": 500000000, "category": "자동차", "tier": 3},
    {"id": "car_4", "name": "부가티 시론", "cost": 4000000000, "category": "자동차", "tier": 4},
    {"id": "art_1", "name": "뱅크시 프린트", "cost": 50000000, "category": "미술품", "tier": 1},
    {"id": "art_2", "name": "앤디워홀 실크스크린", "cost": 500000000, "category": "미술품", "tier": 2},
    {"id": "yacht_1", "name": "세일링 요트", "cost": 1000000000, "category": "기타", "tier": 2},
    {"id": "jet_1", "name": "개인 제트기", "cost": 30000000000, "category": "기타", "tier": 4},
]

# ============================================================
# 4. 세금 & 금리 시스템
# ============================================================
TAX_BRACKETS = [
    (0, 12000000, 0.06),           # 1200만원 이하: 6%
    (12000000, 46000000, 0.15),     # ~4600만: 15%
    (46000000, 88000000, 0.24),     # ~8800만: 24%
    (88000000, 150000000, 0.35),    # ~1.5억: 35%
    (150000000, 300000000, 0.38),   # ~3억: 38%
    (300000000, 500000000, 0.40),   # ~5억: 40%
    (500000000, 1000000000, 0.42),  # ~10억: 42%
    (1000000000, float('inf'), 0.45), # 10억 초과: 45%
]

BASE_INTEREST_RATES = {
    "2020": 0.50, "2021": 0.75, "2022": 3.50, 
    "2023": 3.50, "2024": 3.00, "2025": 2.75,
}

def calc_tax(profit):
    """양도소득세 계산 (누진세율)"""
    if profit <= 0: return 0
    tax = 0
    remaining = profit
    for low, high, rate in TAX_BRACKETS:
        if remaining <= 0: break
        taxable = min(remaining, high - low)
        tax += taxable * rate
        remaining -= taxable
    return int(tax)

def get_interest_rate(date_str):
    """해당 연도의 기준금리"""
    year = date_str[:4]
    return BASE_INTEREST_RATES.get(year, 3.0)

# ============================================================
# 5. 엔딩 시스템
# ============================================================
ENDINGS = {
    "tycoon": {
        "title": "🏆 재벌 엔딩", "condition": "총 자산 1000억 달성",
        "desc": "당신은 대한민국을 대표하는 투자의 전설이 되었습니다.", "threshold": 100000000000,
    },
    "rich": {
        "title": "💰 부자 엔딩", "condition": "총 자산 100억 달성",
        "desc": "안정적인 부를 일군 성공한 투자자입니다.", "threshold": 10000000000,
    },
    "investor": {
        "title": "📈 투자자 엔딩", "condition": "총 자산 10억 달성",
        "desc": "꾸준한 투자로 자산을 불렸습니다. 훌륭합니다!", "threshold": 1000000000,
    },
    "survivor": {
        "title": "😐 생존자 엔딩", "condition": "원금 유지",
        "desc": "잃지 않는 것도 실력입니다... 아마도.", "threshold": 10000000,
    },
    "bankrupt": {
        "title": "💀 파산 엔딩", "condition": "총 자산 100만원 이하",
        "desc": "모든 것을 잃었습니다. 하지만 경험은 남았죠...", "threshold": 0,
    },
    "honor": {
        "title": "🎖️ 명예 엔딩", "condition": "100억 이상 기부",
        "desc": "부를 나눈 진정한 승자. 당신의 이름은 영원히 기억됩니다.", "threshold": -1,
    },
}

# ============================================================
# Asset 클래스 (수정된 완전판)
# ============================================================
_stock_data_cache = None
def _load_stock_data_cached():
    global _stock_data_cache
    if _stock_data_cache is not None:
        return _stock_data_cache
    import os
    paths = ["stock_data.json"]
    try:
        paths.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "stock_data.json"))
    except: pass
    paths.extend(["./stock_data.json", "../stock_data.json"])
    for p in paths:
        try:
            with open(p, "r", encoding="utf-8") as f:
                _stock_data_cache = json.load(f)
            print(f"  stock_data.json loaded from: {p}")
            return _stock_data_cache
        except: continue
    print("  WARNING: stock_data.json not found!")
    _stock_data_cache = {}
    return _stock_data_cache

class Asset:
    def __init__(self, name, ticker, currency="KRW", sector="Default"):
        self.name = name
        self.ticker = ticker
        self.currency = currency
        self.sector = sector
        
        self.price_map = {}
        self.dates_list = []
        
        # JSON 데이터 로드 (캐시 사용)
        try:
            full_data = _load_stock_data_cached()
            if ticker in full_data:
                self.price_map = full_data[ticker]
                self.dates_list = sorted(list(self.price_map.keys()))
                print(f"  [{name}] loaded ({len(self.dates_list)} days)")
            else:
                print(f"  [{name}] no data for {ticker}")
        except Exception as e:
            print(f"  [{name}] load error: {e}")

        self.candles = []
        self.price = 0
        self.prev_close = 0
        self.change_rate = 0.0
        self.current_date_str = ""
        self.trade_log = []

    def set_date(self, date_str):
        self.current_date_str = date_str
        if date_str in self.price_map:
            # JSON 데이터에서 가져오기
            data = self.price_map[date_str]
            self.price = data['close']
            
            # 전일 종가 (간이 계산: 오늘 시가와 비슷하다고 가정하거나 데이터가 있으면 사용)
            self.prev_close = data.get('open', self.price) 
            if self.prev_close == 0: self.prev_close = self.price
            
            # 등락률 계산
            self.change_rate = ((self.price - self.prev_close) / self.prev_close) * 100 if self.prev_close != 0 else 0.0
            
            # 캔들 추가 (차트용)
            candle = {
                'open': data['open'], 'high': data['high'],
                'low': data['low'], 'close': data['close'],
                'date': date_str
            }
            self.candles.append(candle)
            if len(self.candles) > 60:  # 차트에는 최근 60개만 유지
                self.candles.pop(0)

    def get_price_krw(self):
        if self.currency == "USD":
            return self.price * USD_RATE
        return self.price

    def add_trade_log(self, qty, type_str):
        self.trade_log.insert(0, {
            "date": self.current_date_str,
            "price": self.get_price_krw(),
            "qty": qty,
            "type": type_str
        })
        if len(self.trade_log) > 10: self.trade_log.pop()

# ============================================================
# 뉴스/이벤트 헬퍼 함수
# ============================================================
def get_available_news(current_date_str, player_skills, lookback_days=7):
    try:
        curr_date = datetime.strptime(current_date_str, "%Y-%m-%d")
    except:
        return []
    
    available = []
    has_premium = "info_insider" in player_skills
    fake_detect = 0.0
    if "info_advanced" in player_skills: fake_detect = 0.5
    if "info_insider" in player_skills: fake_detect = 0.9
    
    for news in TIMELINE_NEWS:
        news_date = datetime.strptime(news['date'], "%Y-%m-%d")
        days_diff = (curr_date - news_date).days
        
        if 0 <= days_diff <= lookback_days:
            if news.get('requires_premium', False) and not has_premium:
                locked_news = news.copy()
                locked_news['locked'] = True
                locked_news['content'] = "🔒 내부자 네트워크 스킬이 필요합니다."
                available.append(locked_news)
                continue
            
            entry = news.copy()
            entry['locked'] = False
            
            if news.get('fake', False):
                if random.random() < fake_detect:
                    entry['detected_fake'] = True
                else:
                    entry['detected_fake'] = False
            else:
                entry['detected_fake'] = False
            
            available.append(entry)
    
    return available

def get_forecast_report(current_date_str, sector):
    try:
        curr_date = datetime.strptime(current_date_str, "%Y-%m-%d")
    except:
        return None

    candidates = []
    for news in TIMELINE_NEWS:
        if news.get('fake', False): continue
        if news['sector'] == sector or news['sector'] == "Default":
            news_date = datetime.strptime(news['date'], "%Y-%m-%d")
            days_diff = (news_date - curr_date).days
            
            if 0 < days_diff <= 90:
                if days_diff <= 7: timeframe = "매우 임박 (1주 내)"
                elif days_diff <= 30: timeframe = "단기 (1달 내)"
                else: timeframe = "중기 (3달 내)"
                
                rpt = news.copy()
                rpt['timeframe'] = timeframe
                candidates.append(rpt)
    
    if not candidates:
        return {
            "title": "특이사항 없음", 
            "content": "당분간 큰 이벤트가 감지되지 않습니다.",
            "price": 50000, "timeframe": "-"
        }
    
    candidates.sort(key=lambda x: x['date'])
    return candidates[0]

# ============================================================
# Player & Rival 클래스
# ============================================================
class Player:
    def __init__(self, initial_cash):
        self.start_cash = initial_cash
        self.cash = initial_cash
        self.portfolio = {}
        self.buy_prices = {}
        self.short_positions = {}
        self.reports = []
        self.skills = {}
        self.skill_points_spent = 0
        self.home = "gosiwon"
        self.collectibles = []
        self.stress = 0
        self.max_stress = 100
        self.health = 100
        self.consecutive_trading_days = 0
        self.total_profit_realized = 0
        self.total_tax_paid = 0
        self.total_fees_paid = 0
        self.loan = 0
        self.loan_interest_paid = 0
        self.total_donated = 0
        self.auto_stoploss = None
        self.auto_takeprofit = None
        self.run_count = 1
        self.permanent_bonus = 0
        self.game_speed = 1
        self.paused = False
        self.notifications = []

    def assign_mission(self, assets):
        missions = [
            {"type": "buy", "target": random.choice(assets).name, "qty": 10, "desc": f"오늘 {random.choice(assets).name} 10주 이상 매수"},
            {"type": "save", "target": None, "qty": 0, "desc": "오늘 하루 지출(손실) 없이 버티기"},
            {"type": "stress", "target": None, "qty": 30, "desc": "스트레스 30 이하로 유지하기"},
        ]
        self.daily_mission = random.choice(missions)
        self.daily_mission["progress"] = 0
        self.daily_mission["completed"] = False
        self.mission_reward = random.randint(10, 50) * 10000 

    def check_mission(self, action_type, asset_name=None, qty=0):
        if not hasattr(self, 'daily_mission') or not self.daily_mission: return False
        if self.daily_mission.get("completed", False): return False
        
        m = self.daily_mission
        if m["type"] == "buy" and action_type == "BUY" and asset_name == m["target"]:
            m["progress"] += qty
            if m["progress"] >= m["qty"]:
                m["completed"] = True
                self.cash += self.mission_reward
                return True
        return False

    def add_notification(self, msg, color=(255, 255, 100), duration=180):
        self.notifications.insert(0, {"msg": msg, "color": color, "timer": duration})
        if len(self.notifications) > 5: self.notifications.pop()
    
    def update_notifications(self):
        for n in self.notifications: n['timer'] -= 1
        self.notifications = [n for n in self.notifications if n['timer'] > 0]

    def get_fee_rate(self):
        base = 0.015
        if "trade_basic" in self.skills: base *= 0.5
        return base

    def buy(self, asset, quantity):
        if quantity <= 0: return False
        price_krw = asset.get_price_krw()
        cost = price_krw * quantity
        fee = cost * self.get_fee_rate()
        total_cost = cost + fee
        
        if self.cash >= total_cost:
            self.cash -= total_cost
            self.total_fees_paid += fee
            prev_qty = self.portfolio.get(asset.name, 0)
            prev_avg = self.buy_prices.get(asset.name, 0)
            new_qty = prev_qty + quantity
            if new_qty > 0:
                self.buy_prices[asset.name] = ((prev_avg * prev_qty) + (price_krw * quantity)) / new_qty
            self.portfolio[asset.name] = round(new_qty, 4)
            asset.add_trade_log(quantity, "BUY")
            if random.random() < 0.2: self.stress = min(self.max_stress, self.stress + 1)
            return True
        return False

    def sell(self, asset, quantity):
        if quantity <= 0: return False
        if self.portfolio.get(asset.name, 0) >= quantity:
            price_krw = asset.get_price_krw()
            earnings = price_krw * quantity
            fee = earnings * self.get_fee_rate()
            net = earnings - fee
            avg_buy = self.buy_prices.get(asset.name, price_krw)
            profit = (price_krw - avg_buy) * quantity
            if profit > 0: self.total_profit_realized += profit
            self.cash += net
            self.total_fees_paid += fee
            self.portfolio[asset.name] = round(self.portfolio.get(asset.name, 0) - quantity, 4)
            if self.portfolio[asset.name] <= 0.0001:
                del self.portfolio[asset.name]
                if asset.name in self.buy_prices: del self.buy_prices[asset.name]
            asset.add_trade_log(quantity, "SELL")
            self.stress = min(self.max_stress, self.stress + 1)
            return True
        return False
    
    def short_sell(self, asset, quantity):
        if "trade_short" not in self.skills: return False
        if quantity <= 0: return False
        price_krw = asset.get_price_krw()
        margin = price_krw * quantity * 0.5
        fee = price_krw * quantity * self.get_fee_rate()
        if self.cash >= margin + fee:
            self.cash -= (margin + fee)
            self.total_fees_paid += fee
            pos = self.short_positions.get(asset.name, {"qty": 0, "entry_price": 0, "margin": 0})
            total_qty = pos["qty"] + quantity
            pos["entry_price"] = ((pos["entry_price"] * pos["qty"]) + (price_krw * quantity)) / total_qty if total_qty > 0 else price_krw
            pos["qty"] = total_qty
            pos["margin"] = pos.get("margin", 0) + margin
            self.short_positions[asset.name] = pos
            asset.add_trade_log(quantity, "SHORT")
            return True
        return False
    
    def close_short(self, asset, quantity):
        pos = self.short_positions.get(asset.name)
        if not pos or pos["qty"] < quantity: return False
        price_krw = asset.get_price_krw()
        profit = (pos["entry_price"] - price_krw) * quantity
        margin_return = pos["margin"] * (quantity / pos["qty"])
        self.cash += margin_return + profit
        if profit > 0: self.total_profit_realized += profit
        pos["qty"] -= quantity
        pos["margin"] -= margin_return
        if pos["qty"] <= 0.0001: del self.short_positions[asset.name]
        else: self.short_positions[asset.name] = pos
        asset.add_trade_log(quantity, "COVER")
        return True

    def take_loan(self, amount, date_str):
        max_loan = self.get_total_value_simple() * 0.5
        if "trade_leverage" in self.skills: max_loan = self.get_total_value_simple() * 1.0
        if self.loan + amount <= max_loan:
            self.loan += amount
            self.cash += amount
            self.add_notification(f"대출 {int(amount):,}원 실행", (100, 200, 255))
            return True
        return False
    
    def repay_loan(self, amount):
        amount = min(amount, self.loan, self.cash)
        if amount > 0:
            self.cash -= amount
            self.loan -= amount
            return True
        return False
    
    def pay_monthly_interest(self, date_str):
        if self.loan > 0:
            rate = get_interest_rate(date_str) / 100.0
            monthly_interest = self.loan * (rate / 12)
            self.cash -= monthly_interest
            self.loan_interest_paid += monthly_interest
            return monthly_interest
        return 0
    
    def pay_monthly_rent(self):
        prop = PROPERTIES.get(self.home, PROPERTIES["gosiwon"])
        self.cash -= prop["monthly_cost"]
        return prop["monthly_cost"]

    def pay_annual_tax(self):
        tax = calc_tax(self.total_profit_realized)
        self.cash -= tax
        self.total_tax_paid += tax
        self.total_profit_realized = 0
        return tax

    def learn_skill(self, skill_id):
        if skill_id in self.skills: return False
        skill = SKILL_TREE.get(skill_id)
        if not skill: return False
        if skill["prereq"] and skill["prereq"] not in self.skills: return False
        if self.cash >= skill["cost"]:
            self.cash -= skill["cost"]
            self.skills[skill_id] = True
            self.skill_points_spent += skill["cost"]
            self.add_notification(f"스킬 습득: {skill['name']}", (100, 255, 100))
            return True
        return False

    def buy_property(self, prop_id):
        prop = PROPERTIES.get(prop_id)
        if not prop: return False
        if PROPERTIES[prop_id]["tier"] <= PROPERTIES[self.home]["tier"]: return False
        if self.cash >= prop["cost"]:
            self.cash -= prop["cost"]
            self.home = prop_id
            self.add_notification(f"🏠 {prop['name']}(으)로 이사!", (255, 215, 0))
            return True
        return False

    def buy_collectible(self, item_id):
        if item_id in self.collectibles: return False
        item = None
        for c in COLLECTIBLES:
            if c["id"] == item_id:
                item = c
                break
        if not item: return False
        if self.cash >= item["cost"]:
            self.cash -= item["cost"]
            self.collectibles.append(item_id)
            self.add_notification(f"🎁 {item['name']} 구매!", (255, 200, 100))
            return True
        return False

    def daily_stress_update(self):
        prop = PROPERTIES.get(self.home, PROPERTIES["gosiwon"])
        recovery = prop["buffs"]["stress_recovery"] * 2 
        if self.cash > 100000000: recovery += 2 
        self.stress = max(0, self.stress - recovery)
        self.consecutive_trading_days += 1
        if self.consecutive_trading_days > 60:
            self.stress = min(100, self.stress + 1)
    
    def take_vacation(self):
        cost = 1000000
        if self.cash >= cost:
            self.cash -= cost
            self.stress = max(0, self.stress - 30)
            self.consecutive_trading_days = 0
            self.add_notification("🏖️ 휴가 다녀왔습니다! 스트레스 감소", (100, 200, 255))
            return True
        return False
    
    def get_stress_debuff(self):
        if self.stress >= 80: return {"order_error_chance": 0.15, "desc": "극심한 스트레스! 주문 실수 15%"}
        elif self.stress >= 60: return {"order_error_chance": 0.05, "desc": "스트레스 높음. 주문 실수 5%"}
        return {"order_error_chance": 0.0, "desc": ""}

    def donate(self, amount):
        if amount > 0 and self.cash >= amount:
            self.cash -= amount
            self.total_donated += amount
            self.stress = max(0, self.stress - 10)
            self.add_notification(f"💝 {int(amount):,}원 기부 완료!", (255, 150, 200))
            return True
        return False

    def get_total_value_simple(self):
        return self.cash

    def get_total_value(self, assets):
        val = self.cash
        for a in assets:
            if a.name in self.portfolio:
                val += a.get_price_krw() * self.portfolio[a.name]
        for a in assets:
            if a.name in self.short_positions:
                pos = self.short_positions[a.name]
                val += pos["margin"]
                val += (pos["entry_price"] - a.get_price_krw()) * pos["qty"]
        val -= self.loan
        return val
    
    def get_net_worth(self, assets):
        val = self.get_total_value(assets)
        prop = PROPERTIES.get(self.home, PROPERTIES["gosiwon"])
        val += prop["cost"]
        for cid in self.collectibles:
            for c in COLLECTIBLES:
                if c["id"] == cid:
                    val += c["cost"]
        return val

    def check_ending(self, assets):
        net = self.get_net_worth(assets)
        if self.total_donated >= 10000000000: return ENDINGS["honor"]
        if net >= 100000000000: return ENDINGS["tycoon"]
        if net >= 10000000000: return ENDINGS["rich"]
        if net >= 1000000000: return ENDINGS["investor"]
        if net <= 1000000: return ENDINGS["bankrupt"]
        return ENDINGS["survivor"]
    
    def run_auto_trades(self, assets):
        if "algo_basic" not in self.skills: return []
        executed = []
        stoploss = self.auto_stoploss if self.auto_stoploss else -5.0
        takeprofit = self.auto_takeprofit if self.auto_takeprofit else None
        
        for a in assets:
            if a.name in self.portfolio and a.name in self.buy_prices:
                avg = self.buy_prices[a.name]
                if avg > 0:
                    pnl_pct = ((a.get_price_krw() - avg) / avg) * 100
                    if pnl_pct <= stoploss:
                        qty = self.portfolio[a.name]
                        if self.sell(a, qty):
                            executed.append(f"🤖 자동 손절: {a.name} {qty}주 매도 ({pnl_pct:.1f}%)")
                    if takeprofit and pnl_pct >= takeprofit:
                        qty = self.portfolio[a.name]
                        if self.sell(a, qty):
                            executed.append(f"🤖 자동 익절: {a.name} {qty}주 매도 ({pnl_pct:.1f}%)")
        return executed
    
    def to_dict(self):
        return {
            "cash": self.cash,
            "portfolio": self.portfolio,
            "buy_prices": self.buy_prices,
            "skills": self.skills,
            "home": self.home,
            "collectibles": self.collectibles,
            "stress": self.stress,
            "run_count": self.run_count,
            "permanent_bonus": self.permanent_bonus,
            "total_donated": self.total_donated,
        }

    def load_from_dict(self, data):
        self.cash = data.get("cash", 10000000)
        self.portfolio = data.get("portfolio", {})
        self.buy_prices = data.get("buy_prices", {})
        self.skills = data.get("skills", {})
        self.home = data.get("home", "gosiwon")
        self.collectibles = data.get("collectibles", [])
        self.stress = data.get("stress", 0)
        self.run_count = data.get("run_count", 1)
        self.permanent_bonus = data.get("permanent_bonus", 0)
        self.total_donated = data.get("total_donated", 0)
        
class Rival:
    def __init__(self, name, style, initial_cash):
        self.name = name
        self.style = style 
        self.total_value = initial_cash
        self.change_rate = 0.0

    def update_daily(self, market_trend):
        base_change = 0.0
        if self.style == "safe":
            base_change = random.uniform(-1.0, 1.5) + (market_trend * 0.5)
        elif self.style == "risky":
            base_change = random.uniform(-5.0, 6.0) + (market_trend * 1.5)
        else:
            base_change = random.uniform(-2.0, 3.0) + market_trend
        percent = base_change / 100
        self.total_value *= (1 + percent)
        self.change_rate = base_change

def create_rivals(start_cash):
    return [
        Rival("여의도 불개미", "risky", start_cash),
        Rival("강남 건물주", "safe", start_cash * 2),
        Rival("AI 단타봇", "balance", start_cash),
        Rival("워렌 버핏", "safe", start_cash * 5),
        Rival("코인 중독자", "risky", start_cash * 0.5),
    ]
