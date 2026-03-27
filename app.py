import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import concurrent.futures
import time

# ==========================================
# 動態掃描池 (Dynamic Watchlist Pool)
# ==========================================
DEFAULT_MARKET_POOL = {
    "US": [
        "AAPL", "MSFT", "NVDA", "TSLA", "AMD", "META", "AMZN", "GOOGL", "AVGO", "PLTR", 
        "SMCI", "ARM", "MU", "INTC", "QCOM", "NFLX", "ADBE", "CRM", "CRWD", "PANW",
        "UBER", "PYPL", "SQ", "COIN", "HOOD", "RIVN", "LCID", "SNOW", "DDOG", "NET",
        "NOW", "INTU", "CSCO", "TXN", "AMAT", "LRCX", "KLAC", "MRVL", "MCHP", "NXPI",
        "ON", "ASML", "CDNS", "SNPS", "FTNT", "MDB", "ZS", "OKTA", "CFLT", "DOCN",
        "MSTR", "MARA", "RIOT", "SOFI", "AFRM", "ROKU", "PINS", "SNAP", "SPOT", "SHOP",
        "MELI", "SE", "BABA", "PDD", "JD", "BIDU", "NTES", "TTD", "RBLX", "U", "APP",
        "DOCU", "ZM", "TWLO", "RNG", "PATH", "AI", "PLUG", "ENPH", "SEDG", "FSLR",
        "RUN", "ALB", "LTHM", "SQM", "V", "MA", "AXP", "JPM", "BAC", "C", "WFC", "GS",
        "MS", "BLK", "SPGI", "MCO", "UNH", "JNJ", "LLY", "MRK", "ABBV", "PFE", "TMO",
        "DHR", "ABT", "UNP", "HON", "BA", "CAT", "DE", "LMT", "RTX", "NOC", "GD",
        "DIS", "CMCSA", "CHTR", "TMUS", "VZ", "T", "NEE", "DUK", "SO",
        "VRT", "GEV", "TNDM", "SPY"
    ],
    "TW": [
        "2330.TW", "2454.TW", "2317.TW", "2382.TW", "3231.TW", "2308.TW", "2881.TW", 
        "2356.TW", "2603.TW", "3443.TW", "3034.TW", "2303.TW", "3661.TW", "3293.TW",
        "3037.TW", "2379.TW", "1519.TW", "2301.TW", "2353.TW", "2324.TW", "2412.TW",
        "2882.TW", "2891.TW", "2886.TW", "2884.TW", "1301.TW", "1303.TW", "2002.TW",
        "1216.TW", "2892.TW", "2885.TW", "2883.TW", "2880.TW", "5871.TW", "2887.TW",
        "5880.TW", "2890.TW", "1101.TW", "1102.TW", "2912.TW", "2615.TW", "2609.TW",
        "2618.TW", "2610.TW", "2395.TW", "2408.TW", "3481.TW", "2409.TW", "6415.TW",
        "3529.TW", "5269.TW", "3008.TW", "3169.TW", "2383.TW", "3017.TW", "2357.TW",
        "3044.TW", "3036.TW", "2376.TW", "6669.TW", "3533.TW", "2313.TW", "2368.TW",
        "6239.TW", "8046.TW", "3042.TW", "3014.TW", "2344.TW", "2449.TW", "8299.TW",
        "3105.TW", "8069.TW", "5347.TW", "6488.TW", "6147.TW", "3260.TW", "3324.TW",
        "3653.TW", "6274.TW", "2352.TW", "2439.TW", "2345.TW", "2455.TW", "2314.TW"
    ],
    "JP": [
        "4063.T", "8035.T", "9984.T", "7203.T", "6861.T", "6758.T", "6920.T", "6501.T",
        "8058.T", "8306.T", "9432.T", "7974.T", "4568.T", "6098.T", "6902.T", "6857.T",
        "6146.T", "6954.T", "6762.T", "6594.T", "6723.T", "6702.T", "7751.T", "7733.T",
        "6981.T", "6753.T", "6503.T", "6502.T", "8031.T", "8001.T", "8002.T", "8053.T",
        "8316.T", "8411.T", "8766.T", "8750.T", "8591.T", "9433.T", "9434.T", "9983.T",
        "4661.T", "3382.T", "9022.T", "9020.T", "4502.T", "4519.T", "4523.T", "4503.T",
        "2502.T", "2802.T", "2914.T", "4452.T", "4911.T", "5108.T", "5401.T", "6301.T",
        "6367.T", "7267.T", "7269.T", "7270.T", "1925.T", "1928.T", "4543.T", "4578.T",
        "4901.T", "5713.T", "6971.T", "7741.T"
    ]
}

def calculate_health_score(info):
    """
    計算財務穩健度分數 (1~5分) - 完全保留原版邏輯
    """
    score = 1 # 基礎分 1 分
    
    if info.get('returnOnEquity', 0) > 0.10: score += 1
    if info.get('currentRatio', 0) > 1.2: score += 1
    if info.get('debtToEquity', 100) < 100: score += 1
    if info.get('revenueGrowth', 0) > 0.05: score += 1
        
    return score

def analyze_stock(ticker, vol_multiplier, min_health, min_upside, detect_oversold):
    """
    兩階段量化引擎：完全保留原版穩定運算邏輯
    """
    try:
        # ==========================================
        # 階段一：技術面掃描
        # ==========================================
        stock_obj = yf.Ticker(ticker)
        data = stock_obj.history(period="3mo")
        
        if data.empty or len(data) < 25:
            return None

        df = pd.DataFrame({
            'Close': data['Close'], 
            'Volume': data['Volume'], 
            'High': data['High'], 
            'Low': data['Low']
        })

        df['5VMA'] = df['Volume'].rolling(window=5).mean()
        
        df['Box_High_20'] = df['High'].shift(1).rolling(window=20).max()
        df['Box_Low_20'] = df['Low'].shift(1).rolling(window=20).min()
        df['Box_Width'] = (df['Box_High_20'] - df['Box_Low_20']) / df['Box_Low_20']
        
        df['20MA'] = df['Close'].rolling(window=20).mean()
        df['STD'] = df['Close'].rolling(window=20).std()
        df['Upper_Band'] = df['20MA'] + (2 * df['STD'])
        df['Lower_Band'] = df['20MA'] - (2 * df['STD'])
        df['Bandwidth'] = (df['Upper_Band'] - df['Lower_Band']) / df['20MA']
        df['Min_BW_10'] = df['Bandwidth'].rolling(window=10).min()

        delta = df['Close'].diff()
        gain = delta.clip(lower=0).ewm(alpha=1/14, min_periods=14, adjust=False).mean()
        loss = -delta.clip(upper=0).ewm(alpha=1/14, min_periods=14, adjust=False).mean()
        rs = gain / loss
        df['RSI_14'] = 100 - (100 / (1 + rs))

        today = df.iloc[-1]
        yesterday = df.iloc[-2]

        is_vol_breakout = today['Volume'] >= (yesterday['5VMA'] * vol_multiplier)
        is_box_breakout = (today['Close'] > today['Box_High_20']) and (today['Box_Width'] < 0.20)
        is_vcp_breakout = (today['Min_BW_10'] < 0.12) and (today['Close'] >= (yesterday['Upper_Band'] * 0.98))
        is_oversold = today['RSI_14'] <= 30

        tech_pattern = None
        if is_box_breakout and is_vol_breakout:
            tech_pattern = "箱型帶量突破 (Box Breakout)"
        elif is_vcp_breakout and is_vol_breakout:
            tech_pattern = "VCP 收斂突破 (Squeeze Breakout)"
        elif detect_oversold and is_oversold:
            tech_pattern = "深度價值 (好股錯殺)"

        if not tech_pattern:
            return None

        # ==========================================
        # 階段二：基本面過濾
        # ==========================================
        info = stock_obj.info
        
        health_score = calculate_health_score(info)
        if health_score < min_health:
            return None 
            
        current_price = today['Close']
        target_price = info.get('targetMeanPrice', current_price) 
        
        if target_price > 0 and current_price > 0:
            upside_pct = ((target_price - current_price) / current_price) * 100
        else:
            upside_pct = 0.0
            
        if upside_pct < min_upside:
            return None 

        # ==========================================
        # 整理結果
        # ==========================================
        name = info.get('shortName', ticker)
        change_pct = ((today['Close'] - yesterday['Close']) / yesterday['Close']) * 100
        
        if "錯殺" in tech_pattern:
            reason_text = f"【技術面】{tech_pattern}，RSI(14) 降至 {round(today['RSI_14'], 1)} 極度超賣區，短期恐慌情緒達標。"
        else:
            reason_text = f"【技術面】{tech_pattern}，成交量為 5日均量的 {round(today['Volume'] / yesterday['5VMA'], 1)} 倍，主力資金明顯介入。"
            
        reason_text += f"<br><br>【基本面】財務穩健度達 {health_score} 分。目前股價低於機構公允價值，潛在上漲空間達 {round(upside_pct, 1)}%。"

        return {
            'ticker': ticker,
            'name': name,
            'price': round(current_price, 2),
            'change_pct': round(change_pct, 2),
            'pattern': tech_pattern,
            'health': health_score,
            'upside': round(upside_pct, 2),
            'fair_value': target_price,
            'rsi': round(today['RSI_14'], 1),
            'volume_ratio': round(today['Volume'] / yesterday['5VMA'], 2),
            'bandwidth': round(today['Bandwidth'] * 100, 2),
            'reason': reason_text,
            'url': f"https://www.tradingview.com/symbols/{ticker.replace('.TW', '').replace('.T', '')}/"
        }

    except Exception as e:
        return None

def main():
    st.set_page_config(page_title="AI 量化動能與價值海選引擎", page_icon="🧠", layout="wide")
    
    # 保留手機版響應式 RWD 樣式設計
    st.markdown("""
        <style>
        .stButton>button { background-color: #3b82f6; color: white; font-weight: bold; border-radius: 8px; font-size: 16px;}
        .stButton>button:hover { background-color: #2563eb; }
        .metric-card { 
            background-color: #1e293b; padding: 24px; border-radius: 12px; 
            border: 1px solid #475569; border-top: 5px solid #3b82f6;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3); min-height: 250px; margin-bottom: 20px;
        }
        .tag-tech { background-color: #047857; color: #d1fae5; padding: 4px 8px; border-radius: 6px; font-size: 12px; font-weight: bold;}
        .tag-health { background-color: #4338ca; color: #e0e7ff; padding: 4px 8px; border-radius: 6px; font-size: 12px; font-weight: bold;}
        .reason-box { background-color: #0f172a; border-left: 4px solid #3b82f6; padding: 12px; margin-top: 16px; border-radius: 4px;}
        
        @media (max-width: 640px) {
            .metric-card h2 { font-size: 1.5rem !important; }
            .tag-tech, .tag-health { font-size: 10px !important; }
            .metric-card p { font-size: 13px !important; }
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("## 🧠 融合 ProPicks AI 邏輯與技術突破的量化引擎")
    st.caption("結合「箱型/VCP 帶量突破」與「財務穩健度/公允價值」的雙重漏斗篩選系統")
    st.divider()

    with st.sidebar:
        st.header("⚙️ 第一層：技術動能篩選")
        # 為提高出表率，預設突破均量微降至 1.1倍
        vol_multiplier = st.slider("突破均量倍數 (預設 1.1倍)", min_value=1.0, max_value=3.0, value=1.1, step=0.1, 
                                   help="突破當日成交量需大於過去5日均量的多少倍？防範假突破的核心。")
        detect_oversold = st.checkbox("🔍 同時尋找「錯殺超跌」標的", value=True, help="納入 RSI(14) 小於 30，且基本面依然優良的深度價值股。")
        
        st.header("🛡️ 第二層：基本面護城河")
        # 為提高出表率，預設穩健度降至 2分
        min_health = st.slider("最低財務穩健度 (1-5分)", min_value=1, max_value=5, value=2,
                               help="基於 ROE、流動比率、負債比與營收成長計算。")
        # 關鍵：預設漲幅設為 0%，避免 yfinance 缺少目標價資料時把股票錯殺
        min_upside = st.slider("最低潛在上漲空間 (%)", min_value=0, max_value=50, value=0, step=5,
                               help="股價距離公允價值 (目標價) 的折價空間，確保安全邊際。設定0可保留未提供目標價的強勢股。")

        st.header("🌍 選擇動態掃描池")
        use_default = st.checkbox("掃描內建美/台/日 280+ 檔權值科技與動能股", value=True)
        custom_tickers = st.text_area("或自行貼上股票代碼 (以逗號分隔)", placeholder="例如: TSLA, AAPL, 2330.TW")
        
        st.divider()
        run_screener = st.button("🚀 啟動雙核心量化海選", use_container_width=True)

    if run_screener:
        scan_list = []
        if use_default:
            scan_list.extend(DEFAULT_MARKET_POOL["US"] + DEFAULT_MARKET_POOL["TW"] + DEFAULT_MARKET_POOL["JP"])
        
        if custom_tickers.strip():
            custom_list = [t.strip() for t in custom_tickers.split(",") if t.strip()]
            scan_list.extend(custom_list)
            
        scan_list = list(set(scan_list))

        if not scan_list:
            st.warning("請選擇內建名單或輸入自訂股票代碼。")
            return

        st.subheader(f"⚡ 正在並行掃描 {len(scan_list)} 檔標的... (將先過濾技術面，再審查財報)")
        start_time = time.time()
        
        final_results = []
        progress_bar = st.progress(0)
        
        # 恢復原版 10 執行緒配置
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_ticker = {executor.submit(analyze_stock, ticker, vol_multiplier, min_health, min_upside, detect_oversold): ticker for ticker in scan_list}
            
            completed = 0
            for future in concurrent.futures.as_completed(future_to_ticker):
                result = future.result()
                if result:
                    final_results.append(result)
                completed += 1
                progress_bar.progress(completed / len(scan_list))
        
        end_time = time.time()
        st.success(f"掃描完成！運算耗時: {round(end_time - start_time, 2)} 秒 | 嚴格篩選後突圍標的：{len(final_results)} 檔")
        st.divider()
        
        if not final_results:
            st.info("🎯 今日全市場沒有標的能同時通過「技術面真突破」與「基本面高分」的雙重考驗。落實量化紀律，空手也是一種策略。")
        else:
            cols = st.columns(3)
            for i, res in enumerate(final_results):
                with cols[i % 3]:
                    if res['ticker'].endswith(".TW"):
                        currency = "NT$"
                    elif res['ticker'].endswith(".T"):
                        currency = "¥"
                    else:
                        currency = "$"
                        
                    pct_color = "#10b981" if res['change_pct'] > 0 else "#ef4444"
                    stars = "⭐" * res['health']
                    
                    html_content = f"""
<div class="metric-card">
<div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 8px;">
<h2 style="color: #60a5fa; margin: 0; font-weight: 800;">{res['ticker']}</h2>
<span class="tag-tech">{res['pattern']}</span>
</div>
<p style="color: #cbd5e1; font-size: 15px; margin: 0 0 12px 0;">{res['name']}</p>
<div style="display: flex; gap: 8px; margin-bottom: 12px;">
<span class="tag-health">穩健度 {stars}</span>
<span class="tag-health">潛在漲幅 {res['upside']}%</span>
</div>
<hr style="border-color: #475569; margin: 12px 0;">
<p style="color: #e2e8f0; font-size: 15px; margin: 6px 0;"><strong>最新收盤價:</strong> <span style="font-size: 22px; color: #ffffff; font-weight: bold; margin-left: 8px;">{currency}{res['price']}</span></p>
<p style="color: #e2e8f0; font-size: 15px; margin: 6px 0;"><strong>今日漲跌幅:</strong> <span style="color: {pct_color}; font-weight: bold; margin-left: 8px;">{res['change_pct']}%</span></p>
<p style="color: #e2e8f0; font-size: 15px; margin: 6px 0;"><strong>公允價值 (目標價):</strong> <span style="color: #94a3b8; margin-left: 8px;">{currency}{res['fair_value']}</span></p>
<div style="background-color: #0f172a; padding: 10px; border-radius: 6px; margin-top: 15px; margin-bottom: 10px;">
<p style="color: #94a3b8; font-size: 12px; margin: 0 0 6px 0;">📊 技術指標狀態</p>
<p style="color: #e2e8f0; font-size: 13px; margin: 4px 0;"><strong>RSI (14):</strong> <span style="color: {'#ef4444' if res['rsi'] <= 30 else '#34d399'}; font-weight: bold;">{res['rsi']}</span> (<=30為超賣)</p>
<p style="color: #e2e8f0; font-size: 13px; margin: 4px 0;"><strong>爆量倍數:</strong> {res['volume_ratio']} 倍</p>
</div>
<div class="reason-box">
<p style="color: #94a3b8; font-size: 12px; margin: 0 0 4px 0; font-weight: bold;">💡 AI 雙核心入選原因</p>
<p style="color: #f8fafc; font-size: 13px; line-height: 1.6; margin: 0;">{res['reason']}</p>
</div>
</div>
"""
                    st.markdown(html_content, unsafe_allow_html=True)
                    st.link_button(f"查看 {res['ticker']} 線圖確認支撐", res['url'], use_container_width=True)

if __name__ == "__main__":
    main()
