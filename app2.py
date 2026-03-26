import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from economy import (
    Asset, Player, get_available_news, PROPERTIES, SKILL_TREE
)

st.set_page_config(page_title="Stock Master Multiplayer", layout="wide")

# ==========================================
# 1. 멀티플레이어 글로벌 서버 & Ready 시스템
# ==========================================
@st.cache_resource
def get_global_server():
    asset_list = [
        ("삼성전자","005930.KS","KRW","Semiconductor"), ("SK하이닉스","000660.KS","KRW","Semiconductor"),
        ("엔비디아","NVDA","USD","Semiconductor"), ("테슬라","TSLA","USD","Auto"),
        ("현대차","005380.KS","KRW","Auto"), ("비트코인","BTC-USD","USD","Crypto"),
        ("삼성바이오","207940.KS","KRW","Bio"), ("애플","AAPL","USD","Default")
    ]
    assets = [Asset(n, t, c, s) for n, t, c, s in asset_list]
    
    all_dates = set()
    for a in assets: all_dates.update(a.dates_list)
    timeline = sorted(list(all_dates))
    start_idx = int(len(timeline) * 0.1)
    
    for i in range(start_idx + 1):
        td = timeline[i]
        for a in assets: a.set_date(td)
        
    return {
        "assets": assets,
        "timeline": timeline,
        "cur_idx": start_idx,
        "players": {},       # 닉네임: Player객체
        "ready_players": set() # 준비 완료를 누른 유저 목록 (NEW!)
    }

server = get_global_server()
assets = server["assets"]
timeline = server["timeline"]

# ==========================================
# 2. 로비 (닉네임 설정 및 접속)
# ==========================================
if "nickname" not in st.session_state:
    st.session_state.nickname = None

if not st.session_state.nickname:
    st.title("🌐 Stock Master: 멀티플레이어 서버")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        with st.container(border=True):
            st.subheader("서버 접속하기")
            nick_input = st.text_input("사용할 닉네임을 입력하세요", max_chars=10)
            # 경고 해결: use_container_width=True 대신 width="stretch" 사용
            if st.button("게임 입장 🚀", width="stretch", type="primary"):
                if nick_input.strip() == "":
                    st.error("닉네임을 입력해주세요!")
                else:
                    if nick_input not in server["players"]:
                        server["players"][nick_input] = Player(10000000)
                    st.session_state.nickname = nick_input
                    st.session_state.selected_stock = "삼성전자"
                    st.session_state.buy_pct = 0.0
                    st.session_state.sell_pct = 0.0
                    st.rerun()
                    
    with col2:
        st.subheader("🏆 현재 접속 중인 플레이어 랭킹")
        if server["players"]:
            ranks = [{"순위": 0, "닉네임": n, "자산": int(p.get_total_value(assets))} for n, p in server["players"].items()]
            ranks.sort(key=lambda x: -x["자산"])
            for i, r in enumerate(ranks): r["순위"] = i + 1
            st.dataframe(pd.DataFrame(ranks), width="stretch", hide_index=True)
        else:
            st.info("아직 접속한 플레이어가 없습니다. 첫 번째 주자가 되어보세요!")
            
    st.stop()

# ==========================================
# 3. 게임 로직 (내 캐릭터 & 시간 진행)
# ==========================================
my_nick = st.session_state.nickname
me = server["players"][my_nick]
cur_idx = server["cur_idx"]
cur_date = timeline[cur_idx] if cur_idx < len(timeline) else "END"

def advance_time(days):
    for _ in range(days):
        if server["cur_idx"] < len(timeline) - 1:
            server["cur_idx"] += 1
            new_date = timeline[server["cur_idx"]]
            for a in assets: a.set_date(new_date)
            for p_name, p_data in server["players"].items():
                p_data.daily_stress_update()
                p_data.run_auto_trades(assets)

# ==========================================
# 4. 사이드바 (시간 제어 & 내 상태)
# ==========================================
with st.sidebar:
    st.title("🕹️ 서버 컨트롤")
    st.markdown(f"**현재 글로벌 날짜:** `{cur_date}`")
    
    st.divider()
    
    # --- 만장일치 Ready 시스템 로직 ---
    total_players = len(server["players"])
    ready_players = len(server["ready_players"])
    
    st.subheader(f"대기열 현황 ({ready_players}/{total_players}명 준비)")
    
    if my_nick in server["ready_players"]:
        st.success("✅ 준비 완료! 다른 플레이어를 기다리는 중입니다...")
    else:
        st.warning("내 턴을 진행하고 준비 버튼을 누르세요.")
        if st.button("✅ 턴 종료 (하루 넘기기 준비)", width="stretch", type="primary"):
            server["ready_players"].add(my_nick)
            # 모두가 준비되었다면 하루를 넘기고 대기열 초기화!
            if len(server["ready_players"]) >= len(server["players"]):
                advance_time(1)
                server["ready_players"].clear()
            st.rerun()
            
    if st.button("🔄 최신 정보 새로고침", width="stretch"):
        st.rerun()
        
    st.divider()
    st.subheader(f"👤 {my_nick}님의 자산")
    tot_val = me.get_total_value(assets)
    profit_rate = (tot_val - me.start_cash) / me.start_cash * 100
    st.metric("총 평가자산", f"{int(tot_val):,}원", f"{profit_rate:+.2f}%")
    st.metric("보유 현금", f"{int(me.cash):,}원")

# ==========================================
# 5. 메인 화면 (거래소 뷰)
# ==========================================
st.title("📈 종합 주식 시장 (Market)")

tab1, tab2, tab3 = st.tabs(["📊 거래소 & 주문", "🏆 서버 전체 랭킹 & 내 포트폴리오", "📰 글로벌 뉴스"])

with tab1:
    st.subheader("전체 시세판")
    cols = st.columns(4)
    for i, a in enumerate(assets):
        with cols[i % 4]:
            chg = a.change_rate
            sign = "+" if chg >= 0 else ""
            is_selected = (st.session_state.selected_stock == a.name)
            
            with st.container(border=True):
                st.metric(label=f"{'⭐ ' if is_selected else ''}{a.name}", value=f"{int(a.get_price_krw()):,}원", delta=f"{sign}{chg:.2f}%")
                if st.button(f"거래하기", key=f"btn_{a.name}", width="stretch", type="primary" if is_selected else "secondary"):
                    st.session_state.selected_stock = a.name
                    st.rerun()

    st.divider()

    selected_asset = next(a for a in assets if a.name == st.session_state.selected_stock)
    st.subheader(f"⚡ [{selected_asset.name}] 분석 및 주문")
    
    chart_col, order_col = st.columns([2.5, 1.5])
    with chart_col:
        if len(selected_asset.candles) > 0:
            df_chart = pd.DataFrame(selected_asset.candles)
            fig = go.Figure(data=[go.Candlestick(
                x=df_chart['date'], open=df_chart['open'], high=df_chart['high'], low=df_chart['low'], close=df_chart['close'],
                increasing_line_color='red', decreasing_line_color='blue'
            )])
            fig.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=400, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, width="stretch")
            
    with order_col:
        with st.container(border=True):
            st.markdown("### 💰 주문창")
            st.markdown(f"**현재가:** `{int(selected_asset.get_price_krw()):,}원`")
            
            buy_tab, sell_tab = st.tabs(["🔴 매수", "🔵 매도"])
            
            with buy_tab:
                st.caption(f"주문가능 현금: {int(me.cash):,}원")
                bc1, bc2, bc3, bc4 = st.columns(4)
                max_buy_qty = me.cash / selected_asset.get_price_krw()
                if bc1.button("10%", key="b1"): st.session_state.buy_pct = max_buy_qty * 0.1
                if bc2.button("25%", key="b2"): st.session_state.buy_pct = max_buy_qty * 0.25
                if bc3.button("50%", key="b3"): st.session_state.buy_pct = max_buy_qty * 0.5
                if bc4.button("MAX", key="b4"): st.session_state.buy_pct = max_buy_qty * 0.99
                
                buy_qty = st.number_input("매수 수량", min_value=0.0, step=1.0, value=float(st.session_state.buy_pct), key="in_buy")
                
                if st.button("매수 주문하기", width="stretch", type="primary"):
                    if me.buy(selected_asset, buy_qty):
                        st.success("체결 완료!")
                        st.session_state.buy_pct = 0.0
                        st.rerun()
                    else:
                        st.error("잔액 부족")
                        
            with sell_tab:
                own_qty = me.portfolio.get(selected_asset.name, 0)
                st.caption(f"매도가능 수량: {own_qty}주")
                sc1, sc2, sc3, sc4 = st.columns(4)
                if sc1.button("10%", key="s1"): st.session_state.sell_pct = own_qty * 0.1
                if sc2.button("25%", key="s2"): st.session_state.sell_pct = own_qty * 0.25
                if sc3.button("50%", key="s3"): st.session_state.sell_pct = own_qty * 0.5
                if sc4.button("MAX", key="s4"): st.session_state.sell_pct = own_qty
                
                sell_qty = st.number_input("매도 수량", min_value=0.0, max_value=float(own_qty), step=1.0, value=float(st.session_state.sell_pct), key="in_sell")
                
                if st.button("매도 주문하기", width="stretch"):
                    if me.sell(selected_asset, sell_qty):
                        st.success("체결 완료!")
                        st.session_state.sell_pct = 0.0
                        st.rerun()
                    else:
                        st.error("수량 부족")

with tab2:
    col_rank, col_port = st.columns([1, 1.5])
    with col_rank:
        st.subheader("🏆 서버 실시간 랭킹")
        ranks = [{"순위": 0, "닉네임": n, "자산": int(p.get_total_value(assets))} for n, p in server["players"].items()]
        ranks.sort(key=lambda x: -x["자산"])
        for i, r in enumerate(ranks): 
            r["순위"] = i + 1
            if r["닉네임"] == my_nick: r["닉네임"] = f"🌟 {r['닉네임']} (나)"
        st.dataframe(pd.DataFrame(ranks), width="stretch", hide_index=True)
        
    with col_port:
        st.subheader("💼 내 포트폴리오")
        holdings = []
        for a in assets:
            q = me.portfolio.get(a.name, 0)
            if q > 0:
                avg = me.buy_prices.get(a.name, 0)
                cur = a.get_price_krw()
                pnl = (cur - avg) / avg * 100 if avg > 0 else 0
                holdings.append({"종목명": a.name, "보유량": round(q, 2), "평가손익": int((cur-avg)*q), "수익률(%)": round(pnl, 2)})
        if holdings:
            st.dataframe(pd.DataFrame(holdings), width="stretch", hide_index=True)
        else:
            st.info("현재 보유 중인 주식이 없습니다.")

with tab3:
    st.subheader("📰 글로벌 뉴스")
    news_list = get_available_news(cur_date, me.skills, lookback_days=14)
    if news_list:
        for n in news_list:
            if n.get('locked'): st.warning(f"🔒 [잠김] {n['title']}")
            elif n.get('fake') and n.get('detected_fake'): st.error(f"⚠ [찌라시] {n['title']} - {n['content']}")
            else: st.info(f"[{n['sector']}] {n['title']} - {n['content']}")
    else:
        st.write("새로운 뉴스가 없습니다.")
