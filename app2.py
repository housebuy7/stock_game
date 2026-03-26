import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from economy import (
    Asset, Player, get_available_news, get_forecast_report,
    PROPERTIES, SKILL_TREE, COLLECTIBLES, get_interest_rate, calc_tax, ENDINGS
)

st.set_page_config(page_title="Stock Master Ultimate", layout="wide", initial_sidebar_state="expanded")

hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ==========================================
# 1. 글로벌 서버 상태 (명예의 전당 추가)
# ==========================================
@st.cache_resource
def get_global_server():
    dummy_assets = [Asset(n, t, c, s) for n, t, c, s in [
        ("삼성전자","005930.KS","KRW","Semiconductor"), ("SK하이닉스","000660.KS","KRW","Semiconductor"),
        ("엔비디아","NVDA","USD","Semiconductor"), ("테슬라","TSLA","USD","Auto"),
        ("현대차","005380.KS","KRW","Auto"), ("비트코인","BTC-USD","USD","Crypto"),
        ("삼성바이오","207940.KS","KRW","Bio"), ("애플","AAPL","USD","Default")
    ]]
    all_dates = set()
    for a in dummy_assets: all_dates.update(a.dates_list)
    timeline = sorted(list(all_dates))
    return {
        "users": {},
        "leaderboard": {},
        "chat_log": [],
        "hall_of_fame": [], # [NEW] 은퇴/파산 유저들의 영구 기록소
        "timeline": timeline,
        "start_idx": int(len(timeline) * 0.1)
    }

server = get_global_server()
timeline = server["timeline"]
start_idx = server["start_idx"]

# ==========================================
# 2. 로비 (로그인)
# ==========================================
if "nickname" not in st.session_state: st.session_state.nickname = None

if not st.session_state.nickname:
    st.title("🏆 Stock Master: 전생 기록 보존")
    st.markdown("비밀번호를 설정해두면 브라우저를 껐다 켜도 자산이 그대로 유지됩니다!")
    
    col1, col2 = st.columns([1, 1.5])
    with col1:
        with st.container(border=True):
            st.subheader("서버 접속 (로그인/가입)")
            nick_input = st.text_input("닉네임", max_chars=10)
            pwd_input = st.text_input("비밀번호 (PIN)", type="password", max_chars=20)
            
            if st.button("게임 시작 🚀", type="primary", use_container_width=True):
                if nick_input.strip() == "" or pwd_input.strip() == "": 
                    st.error("닉네임과 비밀번호를 모두 입력해주세요!")
                else:
                    if nick_input in server["users"]:
                        if server["users"][nick_input]["pwd"] == pwd_input:
                            st.session_state.nickname = nick_input
                            st.session_state.player = server["users"][nick_input]["player"]
                            st.session_state.assets = server["users"][nick_input]["assets"]
                            st.session_state.cur_idx = server["users"][nick_input]["cur_idx"]
                            st.session_state.history_chart = server["users"][nick_input]["history"]
                            st.session_state.game_over = server["users"][nick_input].get("game_over", False)
                            st.session_state.ending_data = server["users"][nick_input].get("ending_data", None)
                            st.session_state.selected_stock = "삼성전자"
                            st.toast(f"환영합니다, {nick_input}님! 이어서 플레이합니다.")
                            st.rerun()
                        else:
                            st.error("❌ 비밀번호가 틀렸습니다. (다른 사람이 선점한 닉네임입니다)")
                    else:
                        st.session_state.nickname = nick_input
                        st.session_state.assets = [Asset(n, t, c, s) for n, t, c, s in [
                            ("삼성전자","005930.KS","KRW","Semiconductor"), ("SK하이닉스","000660.KS","KRW","Semiconductor"),
                            ("엔비디아","NVDA","USD","Semiconductor"), ("테슬라","TSLA","USD","Auto"),
                            ("현대차","005380.KS","KRW","Auto"), ("비트코인","BTC-USD","USD","Crypto"),
                            ("삼성바이오","207940.KS","KRW","Bio"), ("애플","AAPL","USD","Default")
                        ]]
                        st.session_state.player = Player(10000000)
                        st.session_state.cur_idx = start_idx
                        st.session_state.history_chart = [] 
                        st.session_state.game_over = False
                        st.session_state.ending_data = None
                        st.session_state.selected_stock = "삼성전자"
                        
                        for i in range(start_idx + 1):
                            for a in st.session_state.assets: a.set_date(timeline[i])
                        
                        server["users"][nick_input] = {
                            "pwd": pwd_input,
                            "player": st.session_state.player,
                            "assets": st.session_state.assets,
                            "cur_idx": st.session_state.cur_idx,
                            "history": st.session_state.history_chart,
                            "game_over": False,
                            "ending_data": None
                        }
                        server["leaderboard"][nick_input] = {"자산": 10000000, "날짜": timeline[start_idx]}
                        server["chat_log"].append(f"🎉 **{nick_input}**님이 주식 시장에 새로 뛰어들었습니다!")
                        st.rerun()
                    
    with col2:
        st.subheader("🔥 실시간 리더보드")
        if server["leaderboard"]:
            df = pd.DataFrame([{"닉네임": k, "평가자산(원)": v["자산"], "진행 중인 날짜": v["날짜"]} for k, v in server["leaderboard"].items()])
            st.dataframe(df.sort_values(by="평가자산(원)", ascending=False).reset_index(drop=True), use_container_width=True)
        else:
            st.info("아직 접속한 플레이어가 없습니다.")
    st.stop()

# ==========================================
# 3. 내 게임 상태 동기화
# ==========================================
me = st.session_state.player
my_assets = st.session_state.assets
cur_idx = st.session_state.cur_idx
cur_date = timeline[cur_idx] if cur_idx < len(timeline) else "END"
my_nick = st.session_state.nickname

def trigger_ending(assets):
    st.session_state.game_over = True
    st.session_state.ending_data = me.check_ending(assets)
    server["users"][my_nick]["game_over"] = True
    server["users"][my_nick]["ending_data"] = st.session_state.ending_data
    st.rerun()

def advance_time(days):
    if st.session_state.game_over: return
    
    for _ in range(days):
        if st.session_state.cur_idx >= len(timeline) - 1:
            trigger_ending(my_assets)
            return
            
        st.session_state.cur_idx += 1
        new_date = timeline[st.session_state.cur_idx]
        
        for a in my_assets: a.set_date(new_date)
        me.daily_stress_update()
        
        if me.get_total_value(my_assets) <= 50000:
            trigger_ending(my_assets)
            return

        auto_trades = me.run_auto_trades(my_assets)
        if auto_trades:
            for t_msg in auto_trades: st.toast(t_msg, icon="🤖")

        month = new_date[:7]
        if "last_month" not in st.session_state: st.session_state.last_month = month
        if month != st.session_state.last_month:
            st.session_state.last_month = month
            rent = me.pay_monthly_rent()
            interest = me.pay_monthly_interest(new_date)
            if rent > 0: st.toast(f"💸 월 생활비 {int(rent):,}원 지출")
            if interest > 0: st.toast(f"🏦 대출 이자 {int(interest):,}원 납부")

        year = new_date[:4]
        if "last_year" not in st.session_state: st.session_state.last_year = year
        if year != st.session_state.last_year:
            st.session_state.last_year = year
            tax = me.pay_annual_tax()
            if tax > 0: st.toast(f"📋 연말정산: 양도소득세 {int(tax):,}원 납부", icon="⚖️")

    net_worth = me.get_net_worth(my_assets)
    server["leaderboard"][my_nick] = {"자산": int(net_worth), "날짜": timeline[st.session_state.cur_idx]}
    server["users"][my_nick]["cur_idx"] = st.session_state.cur_idx
    
    st.session_state.history_chart.append({"Date": timeline[st.session_state.cur_idx], "NetWorth": net_worth})
    if len(st.session_state.history_chart) > 100: st.session_state.history_chart.pop(0)
    server["users"][my_nick]["history"] = st.session_state.history_chart
    
    if me.notifications:
        for n in me.notifications: st.toast(n['msg'])
        me.notifications = []

def send_chat():
    msg = st.session_state.chat_input
    if msg:
        server["chat_log"].append(f"💬 **{my_nick}**: {msg}")
        if len(server["chat_log"]) > 30: server["chat_log"].pop(0)
        st.session_state.chat_input = ""

# [수정된 환생 로직]
    if st.button("🔄 기록을 남기고 새로운 인생 시작 (환생)", type="primary"):
        server["hall_of_fame"].append({
            "닉네임": my_nick,
            "최종 자산": int(tot),
            "엔딩 칭호": ed['title'],
            "종료 일자": timeline[st.session_state.cur_idx]
        })
        
        # [NEW] 환생 특전 계산 (원본 main.py 로직 완벽 복구)
        # 이전 자산의 1%를 다음 생의 초기 자본금으로 추가 (최대 5,000만 원 한도)
        carry_over_bonus = min(50000000, int(tot * 0.01))
        new_start_cash = 10000000 + me.permanent_bonus + carry_over_bonus
        
        # 새로운 플레이어 객체 생성 (보너스 및 회차 적용)
        new_player = Player(new_start_cash)
        new_player.permanent_bonus = me.permanent_bonus + carry_over_bonus
        new_player.run_count = me.run_count + 1
        
        st.session_state.player = new_player
        st.session_state.assets = [Asset(n, t, c, s) for n, t, c, s in [
            ("삼성전자","005930.KS","KRW","Semiconductor"), ("SK하이닉스","000660.KS","KRW","Semiconductor"),
            ("엔비디아","NVDA","USD","Semiconductor"), ("테슬라","TSLA","USD","Auto"),
            ("현대차","005380.KS","KRW","Auto"), ("비트코인","BTC-USD","USD","Crypto"),
            ("삼성바이오","207940.KS","KRW","Bio"), ("애플","AAPL","USD","Default")
        ]]
        st.session_state.cur_idx = start_idx
        st.session_state.history_chart = []
        st.session_state.game_over = False
        st.session_state.ending_data = None
        
        for i in range(start_idx + 1):
            for a in st.session_state.assets: a.set_date(timeline[i])
            
        server["users"][my_nick]["player"] = st.session_state.player
        server["users"][my_nick]["assets"] = st.session_state.assets
        server["users"][my_nick]["cur_idx"] = st.session_state.cur_idx
        server["users"][my_nick]["history"] = st.session_state.history_chart
        server["users"][my_nick]["game_over"] = False
        server["users"][my_nick]["ending_data"] = None
        server["leaderboard"][my_nick] = {"자산": new_start_cash, "날짜": timeline[start_idx]} # 시작 랭킹 갱신
        
        st.toast(f"✨ 환생 특전! {int(new_start_cash):,}원으로 새 인생을 시작합니다. ({new_player.run_count}회차)")
        st.rerun()

# ==========================================
# 4. 사이드바
# ==========================================
with st.sidebar:
    st.title("🕹️ 상태창")
    st.markdown(f"**현재 날짜:** `{cur_date}`")
    
    col_t1, col_t2, col_t3 = st.columns(3)
    if col_t1.button("+1일"): advance_time(1); st.rerun()
    if col_t2.button("+7일"): advance_time(7); st.rerun()
    if col_t3.button("+30일"): advance_time(30); st.rerun()
        
    st.divider()
    
    tot_val = me.get_net_worth(my_assets)
    profit_rate = (tot_val - me.start_cash) / me.start_cash * 100
    st.metric("💰 총 순자산 (빚 제외)", f"{int(tot_val):,}원", f"{profit_rate:+.2f}%")
    st.metric("💵 가용 현금", f"{int(me.cash):,}원")
    if me.loan > 0: st.metric("🏦 대출 잔액", f"-{int(me.loan):,}원")
    
    st.progress(me.stress / 100, text=f"🤯 스트레스 ({me.stress}%)")
    if me.stress >= 80: st.error("스트레스가 극심합니다! 휴가 혹은 안정이 필요합니다.")
    
    if len(st.session_state.history_chart) > 1:
        st.line_chart(pd.DataFrame(st.session_state.history_chart).set_index("Date"), height=150)
        
    st.divider()
    
    st.subheader("🌐 글로벌 채팅")
    chat_container = st.container(height=200)
    for c in server["chat_log"]: chat_container.markdown(c)
    st.text_input("메시지 입력 (Enter)", key="chat_input", on_change=send_chat)
    if st.button("🔄 서버 동기화"): st.rerun()

# ==========================================
# 5. 메인 화면 (명예의 전당 탭 추가)
# ==========================================
st.title("📈 Stock Master: Ultimate")

# [NEW] 명예의 전당 탭 추가
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 주식 거래소", "💼 내 포트폴리오", "🏦 은행 & 부동산", "⚡ 스킬 & 수집품", "📰 뉴스 & 리포트", "🎖️ 명예의 전당"
])

# ----------------------------------------
# TAB 1: 주식 거래소 (에러 없는 깔끔한 버전)
# ----------------------------------------
with tab1:
    st.subheader("전체 시세판")
    cols = st.columns(4)
    for i, a in enumerate(my_assets):
        with cols[i % 4]:
            chg = a.change_rate
            sign = "+" if chg >= 0 else ""
            is_selected = (st.session_state.selected_stock == a.name)
            with st.container(border=True):
                st.metric(label=f"{'⭐ ' if is_selected else ''}{a.name}", value=f"{int(a.get_price_krw()):,}원", delta=f"{sign}{chg:.2f}%")
                if st.button(f"차트 보기", key=f"btn_{a.name}", type="primary" if is_selected else "secondary"):
                    st.session_state.selected_stock = a.name
                    st.rerun()

    st.divider()

    selected_asset = next(a for a in my_assets if a.name == st.session_state.selected_stock)
    st.subheader(f"⚡ [{selected_asset.name}] 상세 분석")
    
    chart_col, order_col = st.columns([2.5, 1.5])
    with chart_col:
        if len(selected_asset.candles) > 0:
            df_chart = pd.DataFrame(selected_asset.candles)
            fig = go.Figure(data=[go.Candlestick(
                x=df_chart['date'], open=df_chart['open'], high=df_chart['high'], low=df_chart['low'], close=df_chart['close'],
                increasing_line_color='#FF5252', decreasing_line_color='#448AFF'
            )])
            fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=450, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
            
    with order_col:
        with st.container(border=True):
            st.markdown(f"### 💰 주문창 (현재가: `{int(selected_asset.get_price_krw()):,}원`)")
            
            trade_tabs = ["🔴 매수", "🔵 매도"]
            if "trade_short" in me.skills: trade_tabs.append("🟣 공매도(Short)")
            if me.short_positions.get(selected_asset.name, {}).get("qty", 0) > 0: trade_tabs.append("🟢 숏 청산(Cover)")
            
            active_tab = st.tabs(trade_tabs)

            # 1. 매수
            with active_tab[0]:
                st.caption(f"현금: {int(me.cash):,}원 (수수료 {me.get_fee_rate()*100:.2f}%)")
                bc1, bc2, bc3, bc4 = st.columns(4)
                cur_price = selected_asset.get_price_krw()
                max_buy = (me.cash / (cur_price * (1 + me.get_fee_rate()))) if cur_price > 0 else 0
                
                if bc1.button("10%", key="b1"): st.session_state.buy_qty = max_buy * 0.1
                if bc2.button("50%", key="b3"): st.session_state.buy_qty = max_buy * 0.5
                if bc3.button("MAX", key="b4"): st.session_state.buy_qty = max_buy * 0.99
                
                buy_input = st.number_input("수량", min_value=0.0, step=1.0, key="buy_qty" if 'buy_qty' in st.session_state else None)
                if st.button("매수 체결", type="primary"):
                    if me.buy(selected_asset, buy_input): st.toast("✅ 매수 완료!"); st.rerun()
                    else: st.error("주문 실패 (잔액 부족)")

            # 2. 매도
            with active_tab[1]:
                own_qty = me.portfolio.get(selected_asset.name, 0)
                st.caption(f"보유량: {own_qty}주")
                sc1, sc2, sc3 = st.columns(3)
                if sc1.button("10%", key="s1"): st.session_state.sell_qty = own_qty * 0.1
                if sc2.button("50%", key="s3"): st.session_state.sell_qty = own_qty * 0.5
                if sc3.button("MAX", key="s4"): st.session_state.sell_qty = own_qty
                
                sell_input = st.number_input("수량", min_value=0.0, max_value=float(own_qty), step=1.0, key="sell_qty" if 'sell_qty' in st.session_state else None)
                if st.button("매도 체결"):
                    if me.sell(selected_asset, sell_input): st.toast("✅ 매도 완료!"); st.rerun()
                    else: st.error("주문 실패")
                    
            # 3. 공매도
            if "trade_short" in me.skills:
                idx = trade_tabs.index("🟣 공매도(Short)")
                with active_tab[idx]:
                    st.caption("공매도: 증거금 50%")
                    max_short = (me.cash / (cur_price * 0.5)) if cur_price > 0 else 0
                    st.button("MAX 숏", on_click=lambda: st.session_state.update(short_qty=max_short*0.99))
                    short_input = st.number_input("숏 수량", min_value=0.0, step=1.0, key="short_qty" if 'short_qty' in st.session_state else None)
                    if st.button("공매도 진입"):
                        if me.short_sell(selected_asset, short_input): st.toast("✅ 숏 진입 완료!"); st.rerun()
                        else: st.error("증거금 부족")
                        
            # 4. 청산
            if "🟢 숏 청산(Cover)" in trade_tabs:
                idx = trade_tabs.index("🟢 숏 청산(Cover)")
                with active_tab[idx]:
                    sq = me.short_positions.get(selected_asset.name, {}).get("qty", 0)
                    st.caption(f"숏 포지션: {sq}주")
                    st.button("전액 청산", on_click=lambda: st.session_state.update(cover_qty=sq))
                    cover_input = st.number_input("청산 수량", min_value=0.0, max_value=float(sq), step=1.0, key="cover_qty" if 'cover_qty' in st.session_state else None)
                    if st.button("포지션 청산"):
                        if me.close_short(selected_asset, cover_input): st.toast("✅ 청산 완료!"); st.rerun()
                        else: st.error("오류 발생")

# ----------------------------------------
# TAB 2: 내 포트폴리오
# ----------------------------------------
with tab2:
    col_port, col_rank = st.columns([1.5, 1])
    with col_port:
        st.subheader("💼 내 주식/공매도 보유 현황")
        holdings = []
        pie_data = [] 
        
        if me.cash > 0: pie_data.append({"자산명": "현금", "평가액": me.cash})
        
        for a in my_assets:
            q = me.portfolio.get(a.name, 0)
            if q > 0:
                avg = me.buy_prices.get(a.name, 0)
                cur = a.get_price_krw()
                pnl = (cur - avg) / avg * 100 if avg > 0 else 0
                eval_amt = cur * q
                holdings.append({"타입":"🟢매수", "종목": a.name, "수량": round(q,2), "평단가": int(avg), "현재가": int(cur), "손익액": int((cur-avg)*q), "수익률": f"{pnl:+.2f}%"})
                pie_data.append({"자산명": a.name, "평가액": eval_amt})
                
            sq = me.short_positions.get(a.name, {}).get("qty", 0)
            if sq > 0:
                entry = me.short_positions[a.name]['entry_price']
                cur = a.get_price_krw()
                pnl = (entry - cur) / entry * 100
                margin = me.short_positions[a.name]['margin'] + (entry - cur) * sq
                holdings.append({"타입":"🟣공매도", "종목": a.name, "수량": round(sq,2), "평단가": int(entry), "현재가": int(cur), "손익액": int((entry-cur)*sq), "수익률": f"{pnl:+.2f}%"})
                if margin > 0: pie_data.append({"자산명": f"{a.name}(숏)", "평가액": margin})
                
        if holdings: 
            st.dataframe(pd.DataFrame(holdings), use_container_width=True, hide_index=True)
            st.markdown("##### 🥧 자산 비중 분포")
            fig_pie = px.pie(pd.DataFrame(pie_data), values='평가액', names='자산명', hole=0.3)
            fig_pie.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300)
            st.plotly_chart(fig_pie, use_container_width=True)
        else: 
            st.info("보유 중인 포지션이 없습니다.")
        
    with col_rank:
        st.subheader("🏆 실시간 글로벌 랭킹")
        ranks = [{"순위": 0, "닉네임": n, "평가자산(원)": v["자산"], "날짜": v["날짜"]} for n, v in server["leaderboard"].items()]
        ranks.sort(key=lambda x: -x["평가자산(원)"])
        for i, r in enumerate(ranks): 
            r["순위"] = i + 1
            if r["닉네임"] == my_nick: r["닉네임"] = f"🌟 {r['닉네임']} (나)"
        st.dataframe(pd.DataFrame(ranks), use_container_width=True, hide_index=True)

# ----------------------------------------
# TAB 3: 은행, 기부 & 부동산
# ----------------------------------------
with tab3:
    c_bank, c_home = st.columns(2)
    with c_bank:
        st.subheader("🏦 제일은행")
        st.markdown(f"**현재 기준금리:** `{get_interest_rate(cur_date)}%`")
        
        net_worth = me.get_net_worth(my_assets)
        max_loan_limit = net_worth * (1.0 if "trade_leverage" in me.skills else 0.5)
        available_loan = max(0, max_loan_limit - me.loan)
        
        st.markdown(f"**총 대출 한도:** `{int(max_loan_limit):,}원` / **현재 대출금:** `{int(me.loan):,}원`")
        st.markdown(f"**💸 추가 대출 가능 금액:** `{int(available_loan):,}원`")
        
        loan_amount = st.number_input("대출/상환할 금액 (원)", min_value=0.0, step=1000000.0, value=0.0)
        col_b1, col_b2 = st.columns(2)
        if col_b1.button("💰 대출 받기", use_container_width=True):
            if loan_amount <= 0: st.error("금액을 입력하세요.")
            elif loan_amount > available_loan: st.error(f"한도({int(available_loan):,}원) 초과!")
            else:
                if me.take_loan(loan_amount, cur_date): st.toast("✅ 대출 승인!"); st.rerun()
                else: st.error("오류 발생")
                
        if col_b2.button("💸 대출 상환", use_container_width=True):
            if loan_amount <= 0: st.error("금액을 입력하세요.")
            else:
                if me.repay_loan(loan_amount): st.toast("✅ 상환 완료!"); st.rerun()
                else: st.error("잔액이 부족하거나 대출금이 없습니다.")
                
        st.divider()
        # [NEW] 누락되었던 기부 시스템 부활!
        st.subheader("🕊️ 자선 단체 기부")
        st.caption("기부는 연말정산 세금 감면 혜택이 있으며, 특별한 엔딩에 영향을 줍니다.")
        donate_amt = st.number_input("기부할 금액 (원)", min_value=0, step=1000000)
        if st.button("기부하기 🤍", use_container_width=True):
            if donate_amt <= 0: st.error("금액을 입력하세요.")
            elif me.cash >= donate_amt:
                me.cash -= donate_amt
                me.total_donated += donate_amt
                st.toast(f"😇 {int(donate_amt):,}원을 기부하셨습니다! (누적: {int(me.total_donated):,}원)")
                st.rerun()
            else:
                st.error("현금이 부족합니다.")

    with c_home:
        # 기존 부동산 코드와 동일 (그대로 유지)
        st.subheader("🏠 부동산 (내 집 마련)")
        st.markdown(f"현재 거주지: **{PROPERTIES.get(me.home, {}).get('name', '고시원')}**")
        
        for pid, p in PROPERTIES.items():
            with st.expander(f"{p['name']} (매입가: {int(p['cost']/10000)}만 / 월세: {int(p['monthly_cost']/10000)}만)"):
                st.write(f"설명: {p['desc']} / 효과: 스트레스 회복 {p['buffs']['stress_recovery']}배")
                if me.home == pid: st.button("현재 거주 중", disabled=True, key=f"p_{pid}")
                elif p['tier'] <= PROPERTIES[me.home]['tier']: st.button("하위 티어 불가", disabled=True, key=f"p_{pid}")
                else:
                    if st.button("이사하기 (매입)", key=f"p_{pid}", type="primary"):
                        if me.buy_property(pid): st.success("이사 완료!"); st.rerun()
                        else: st.error("자금이 부족합니다.")

# ----------------------------------------
# TAB 4: 스킬 & 수집품
# ----------------------------------------
with tab4:
    c_skill, c_item = st.columns(2)
    with c_skill:
        st.subheader("⚡ 스킬 트리")
        for sid, s in SKILL_TREE.items():
            with st.container(border=True):
                st.markdown(f"**{s['name']}** - {s['desc']}")
                if sid in me.skills: st.button("✅ 습득 완료", disabled=True, key=f"sk_{sid}")
                else:
                    if st.button(f"배우기 ({int(s['cost']/10000)}만 원)", key=f"sk_{sid}"):
                        if me.learn_skill(sid): st.success("스킬 습득!"); st.rerun()
                        else: st.error("자금 부족 또는 선행 스킬 필요!")
    
    with c_item:
        st.subheader("💎 사치품 컬렉션")
        for item in COLLECTIBLES:
            with st.container(border=True):
                col_i1, col_i2 = st.columns([3, 1])
                col_i1.markdown(f"**{item['name']}** ({item['category']}) - {int(item['cost']/10000)}만 원")
                if item['id'] in me.collectibles: col_i2.button("소유함", disabled=True, key=f"it_{item['id']}")
                else:
                    if col_i2.button("구매", key=f"it_{item['id']}"):
                        if me.buy_collectible(item['id']): st.success("구매 완료!"); st.rerun()
                        else: st.error("잔고 부족!")

# ----------------------------------------
# TAB 5: 뉴스 & 리포트
# ----------------------------------------
with tab5:
    c_news, c_report = st.columns([2, 1])
    with c_news:
        st.subheader("📰 오늘의 뉴스")
        news_list = get_available_news(cur_date, me.skills, lookback_days=14)
        if news_list:
            for n in news_list:
                if n.get('locked'): st.warning(f"🔒 [잠김] 내부자 정보 (스킬 필요)")
                elif n.get('fake') and n.get('detected_fake'): st.error(f"⚠ [찌라시] {n['title']} - {n['content']}")
                else: st.info(f"[{n['sector']}] {n['title']} - {n['content']}")
        else: st.write("새로운 뉴스가 없습니다.")
        
    with c_report:
        st.subheader("🛒 프리미엄 리포트 구매")
        for sec, name in [("Semiconductor", "반도체"), ("Auto", "자동차"), ("Crypto", "암호화폐"), ("Bio", "바이오")]:
            rp = get_forecast_report(cur_date, sec)
            cost = rp['price'] if rp else 50000
            if st.button(f"{name} 리포트 구매 ({int(cost/10000)}만)"):
                if rp and me.cash >= cost:
                    me.cash -= cost
                    st.success(f"[{rp['timeframe']}] {rp['title']} - {rp['content']}")
                elif rp: st.error("잔액 부족")
                else: st.info("해당 섹터에 임박한 큰 이벤트가 없습니다.")

# ----------------------------------------
# TAB 6: 명예의 전당 (새로 추가됨!)
# ----------------------------------------
with tab6:
    st.subheader("🎖️ 서버 명예의 전당")
    st.caption("파산하거나 게임을 완주한 전설적인 투자자들의 기록입니다.")
    if server["hall_of_fame"]:
        hof_df = pd.DataFrame(server["hall_of_fame"])
        # 자산 기준으로 내림차순 정렬
        hof_df = hof_df.sort_values(by="최종 자산", ascending=False).reset_index(drop=True)
        hof_df.index += 1
        st.dataframe(hof_df, use_container_width=True)
    else:
        st.info("아직 역사를 남긴 투자자가 없습니다. 첫 번째 전설이 되어보세요!")
