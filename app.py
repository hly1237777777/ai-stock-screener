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
        "1101.TW", "1102.TW", "1216.TW", "1301.TW", "1303.TW", "1304.TW", "1305.TW", "1308.TW", 
        "1519.TW", "1528.TW", "1582.TW", "1708.TW", "1727.TW", "1785.TW", "1802.TW", "1815.TW", 
        "1905.TW", "2002.TW", "2301.TW", "2303.TW", "2305.TW", "2308.TW", "2313.TW", "2314.TW", 
        "2317.TW", "2324.TW", "2327.TW", "2330.TW", "2337.TW", "2344.TW", "2345.TW", "2352.TW", 
        "2353.TW", "2355.TW", "2356.TW", "2357.TW", "2360.TW", "2367.TW", "2368.TW", "2376.TW", 
        "2379.TW", "2382.TW", "2383.TW", "2395.TW", "2404.TW", "2406.TW", "2408.TW", "2409.TW", 
        "2412.TW", "2413.TW", "2419.TW", "2439.TW", "2449.TW", "2454.TW", "2455.TW", "2484.TW", 
        "2489.TW", "2603.TW", "2605.TW", "2609.TW", "2610.TW", "2615.TW", "2618.TW", "2880.TW", 
        "2881.TW", "2882.TW", "2883.TW", "2884.TW", "2885.TW", "2886.TW", "2887.TW", "2890.TW", 
        "2891.TW", "2892.TW", "2912.TW", "3008.TW", "3014.TW", "3017.TW", "3026.TW", "3034.TW", 
        "3036.TW", "3037.TW", "3042.TW", "3044.TW", "3062.TW", "3081.TW", "3105.TW", "3131.TW", 
        "3135.TW", "3138.TW", "3149.TW", "3169.TW", "3211.TW", "3221.TW", "3231.TW", "3260.TW", 
        "3293.TW", "3324.TW", "3339.TW", "3443.TW", "3450.TW", "3481.TW", "3491.TW", "3498.TW", 
        "3529.TW", "3533.TW", "3563.TW", "3615.TW", "3653.TW", "3661.TW", "3665.TW", "3711.TW", 
        "3715.TW", "4720.TW", "4741.TW", "4903.TW", "4906.TW", "4908.TW", "4919.TW", "4931.TW", 
        "4949.TW", "4956.TW", "4958.TW", "4967.TW", "4971.TW", "4977.TW", "4989.TW", "5243.TW", 
        "5269.TW", "5274.TW", "5291.TW", "5347.TW", "5439.TW", "5871.TW", "5880.TW", "6127.TW", 
        "6139.TW", "6147.TW", "6163.TW", "6187.TW", "6213.TW", "6223.TW", "6239.TW", "6274.TW", 
        "6285.TW", "6415.TW", "6442.TW", "6443.TW", "6488.TW", "6530.TW", "6588.TW", "6640.TW", 
        "6669.TW", "6672.TW", "6706.TW", "6770.TW", "6788.TW", "6821.TW", "6830.TW", "7547.TW", 
        "7709.TW", "7717.TW", "7728.TW", "7769.TW", "7810.TW", "8021.TW", "8027.TW", "8028.TW", 
        "8046.TW", "8064.TW", "8069.TW", "8096.TW", "8289.TW", "8299.TW", "8358.TW", "8996.TW"
    ],
    "JP": [
        "1605.T", "1925.T", "1928.T", "2181.T", "2502.T", "2802.T", "285A.T", "2914.T", 
        "3103.T", "3315.T", "3350.T", "3382.T", "3402.T", "3436.T", "3697.T", "4005.T", 
        "4063.T", "4188.T", "4452.T", "4502.T", "4503.T", "4506.T", "4519.T", "4523.T", 
        "4543.T", "4564.T", "4568.T", "4578.T", "4594.T", "4597.T", "4661.T", "4689.T", 
        "4755.T", "4888.T", "4901.T", "4911.T", "5016.T", "5020.T", "5108.T", "5202.T", 
        "523A.T", "5401.T", "5713.T", "5801.T", "5802.T", "5803.T", "5831.T", "5856.T", 
        "6072.T", "6098.T", "6146.T", "6178.T", "6301.T", "6366.T", "6367.T", "6501.T", 
        "6502.T", "6503.T", "6522.T", "6526.T", "6594.T", "6613.T", "6701.T", "6702.T", 
        "6723.T", "6740.T", "6752.T", "6753.T", "6758.T", "6762.T", "6857.T", "6861.T", 
        "6902.T", "6920.T", "6954.T", "6971.T", "6981.T", "6993.T", "7011.T", "7013.T", 
        "7182.T", "7201.T", "7203.T", "7205.T", "7211.T", "7261.T", "7267.T", "7269.T", 
        "7270.T", "7272.T", "7532.T", "7733.T", "7741.T", "7751.T", "7974.T", "8001.T", 
        "8002.T", "8031.T", "8035.T", "8053.T", "8058.T", "8113.T", "8267.T", "8306.T", 
        "8308.T", "8316.T", "8410.T", "8411.T", "8473.T", "8591.T", "8601.T", "8604.T", 
        "8729.T", "8750.T", "8766.T", "8801.T", "8918.T", "9020.T", "9022.T", "9104.T", 
        "9107.T", "9432.T", "9433.T", "9434.T", "9501.T", "9831.T", "9983.T", "9984.T"
    ]
}

def calculate_health_score(info):
    """
    計算財務穩健度分數 (1~5分) - 模擬 ProPicks 邏輯
    根據獲利能力、現金流、成長性、負債狀況給分
    """
    score = 1 # 基礎分 1 分
    
    # 1. 獲利能力：股東權益報酬率 (ROE) > 10%
    if info.get('returnOnEquity', 0) > 0.10: score += 1
    # 2. 流動性/現金流：流動比率 > 1.2
    if info.get('currentRatio', 0) > 1.2: score += 1
    # 3. 財務槓桿：負債權益比 < 100% (越低越好，若為空值也當作過關)
    if info.get('debtToEquity', 100) < 100: score += 1
    # 4. 成長性：營收成長率 > 5%
    if info.get('revenueGrowth', 0) > 0.05: score += 1
        
    return score

def analyze_stock(ticker, vol_multiplier, min_health, min_upside, detect_oversold):
    """
    兩階段量化引擎：
    階段一：掃描「箱型突破」、「VCP壓縮突破」或「深度價值(錯殺)」
    階段二：獲取基本面計算「公允價值」與「穩健度」
    """
    try:
        # ==========================================
        # 階段一：技術面掃描 (修正為執行緒安全的 history API)
        # ==========================================
        stock_obj = yf.Ticker(ticker)
        data = stock_obj.history(period="3mo")
        
        if data.empty or len(data) < 25:
            return None

        # history() API 格式固定，直接讀取不需處理 MultiIndex，且保障多執行緒資料不重疊
        df = pd.DataFrame({
            'Close': data['Close'], 
            'Volume': data['Volume'], 
            'High': data['High'], 
            'Low': data['Low']
        })

        # 計算 5VMA
        df['5VMA'] = df['Volume'].rolling(window=5).mean()
        
        # --- 型態 A：箱型突破 (Box Breakout) 演算法 ---
        # 尋找過去 20 天 (不含今日) 的最高與最低價形成的箱型
        df['Box_High_20'] = df['High'].shift(1).rolling(window=20).max()
        df['Box_Low_20'] = df['Low'].shift(1).rolling(window=20).min()
        # 箱型不能太寬 (例如上下振幅不超過 15%)，代表籌碼穩定換手
        df['Box_Width'] = (df['Box_High_20'] - df['Box_Low_20']) / df['Box_Low_20']
        
        # --- 型態 B：VCP (布林通道) 壓縮突破演算法 ---
        df['20MA'] = df['Close'].rolling(window=20).mean()
        df['STD'] = df['Close'].rolling(window=20).std()
        df['Upper_Band'] = df['20MA'] + (2 * df['STD'])
        df['Lower_Band'] = df['20MA'] - (2 * df['STD'])
        df['Bandwidth'] = (df['Upper_Band'] - df['Lower_Band']) / df['20MA']
        df['Min_BW_10'] = df['Bandwidth'].rolling(window=10).min()

        # --- 型態 C：深度價值 (錯殺超跌 RSI) 演算法 ---
        delta = df['Close'].diff()
        gain = delta.clip(lower=0).ewm(alpha=1/14, min_periods=14, adjust=False).mean()
        loss = -delta.clip(upper=0).ewm(alpha=1/14, min_periods=14, adjust=False).mean()
        rs = gain / loss
        df['RSI_14'] = 100 - (100 / (1 + rs))

        today = df.iloc[-1]
        yesterday = df.iloc[-2]

        # 判斷突破與量能
        is_vol_breakout = today['Volume'] >= (yesterday['5VMA'] * vol_multiplier)
        
        # 箱型突破條件：今日收盤突破箱頂，且箱型寬度 < 20%
        is_box_breakout = (today['Close'] > today['Box_High_20']) and (today['Box_Width'] < 0.20)
        
        # VCP突破條件：近期極度壓縮 (<12%) 且今日逼近或突破上軌
        is_vcp_breakout = (today['Min_BW_10'] < 0.12) and (today['Close'] >= (yesterday['Upper_Band'] * 0.98))

        # 超賣條件：RSI(14) 小於等於 30
        is_oversold = today['RSI_14'] <= 30

        tech_pattern = None
        if is_box_breakout and is_vol_breakout:
            tech_pattern = "箱型帶量突破 (Box Breakout)"
        elif is_vcp_breakout and is_vol_breakout:
            tech_pattern = "VCP 收斂突破 (Squeeze Breakout)"
        elif detect_oversold and is_oversold:
            tech_pattern = "深度價值 (好股錯殺)"

        # 如果技術面沒有發動，直接放棄，節省運算時間
        if not tech_pattern:
            return None

        # ==========================================
        # 階段二：基本面過濾 (模擬 ProPicks 核心指標)
        # ==========================================
        # stock_obj 已經在最上方階段一宣告過了，直接使用即可
        info = stock_obj.info
        
        # 1. 財務穩健度計算
        health_score = calculate_health_score(info)
        if health_score < min_health:
            return None # 剔除地雷股
            
        # 2. 公允價值潛在上漲空間 (以分析師平均目標價代替)
        current_price = today['Close']
        target_price = info.get('targetMeanPrice', current_price) # 若無資料則預設無漲幅
        
        if target_price > 0 and current_price > 0:
            upside_pct = ((target_price - current_price) / current_price) * 100
        else:
            upside_pct = 0.0
            
        if upside_pct < min_upside:
            return None # 剔除無上漲空間的股票

        # ==========================================
        # 整理通過所有嚴格測試的結果
        # ==========================================
        name = info.get('shortName', ticker)
        change_pct = ((today['Close'] - yesterday['Close']) / yesterday['Close']) * 100
        
        # 決定入選原因的文案 (將 \n 換成 HTML 的 <br> 標籤以防 Markdown 破版)
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

def render_stock_card(res):
    """輔助函式：渲染單一股票卡片 HTML"""
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

def main():
    st.set_page_config(page_title="AI 量化動能與價值海選引擎", page_icon="🧠", layout="wide")
    
    st.markdown("""
        <style>
        .stButton>button { background-color: #3b82f6; color: white; font-weight: bold; border-radius: 8px; font-size: 16px;}
        .stButton>button:hover { background-color: #2563eb; }
        .metric-card { 
            background-color: #1e293b; padding: 24px; border-radius: 12px; 
            border: 1px solid #475569; border-top: 5px solid #3b82f6;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3); height: 100%; margin-bottom: 20px;
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
        vol_multiplier = st.slider("突破均量倍數 (預設 1.2倍)", min_value=1.0, max_value=3.0, value=1.2, step=0.1, 
                                   help="突破當日成交量需大於過去5日均量的多少倍？防範假突破的核心。")
        detect_oversold = st.checkbox("🔍 同時尋找「錯殺超跌」標的", value=True, help="納入 RSI(14) 小於 30，且基本面依然優良的深度價值股。")
        
        st.header("🛡️ 第二層：基本面護城河")
        min_health = st.slider("最低財務穩健度 (1-5分)", min_value=1, max_value=5, value=3,
                               help="基於 ROE、流動比率、負債比與營收成長計算。3分以上代表財務健康。")
        min_upside = st.slider("最低潛在上漲空間 (%)", min_value=0, max_value=50, value=10, step=5,
                               help="股價距離公允價值 (目標價) 的折價空間，確保安全邊際。")

        st.header("🌍 選擇動態掃描池")
        use_default = st.checkbox("掃描內建美/台/日 最新擴充之權值科技與動能股", value=True)
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
            
        # 移除重複代碼
        scan_list = list(set(scan_list))

        if not scan_list:
            st.warning("請選擇內建名單或輸入自訂股票代碼。")
            return

        st.subheader(f"⚡ 正在並行掃描 {len(scan_list)} 檔標的... (將先過濾技術面，再審查財報)")
        start_time = time.time()
        
        final_results = []
        progress_bar = st.progress(0)
        
        # 多執行緒平行運算
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
            # 建立分類清單
            us_stocks = []
            tw_stocks = []
            jp_stocks = []
            
            for res in final_results:
                if res['ticker'].endswith(".TW"):
                    tw_stocks.append(res)
                elif res['ticker'].endswith(".T"):
                    jp_stocks.append(res)
                else:
                    us_stocks.append(res)
            
            # 建立 左/中/右 三個垂直欄位
            col_us, col_tw, col_jp = st.columns(3)
            
            with col_us:
                st.subheader(f"🇺🇸 美股 ({len(us_stocks)})")
                if not us_stocks:
                    st.caption("無符合條件之標的")
                for res in us_stocks:
                    render_stock_card(res)
                    
            with col_tw:
                st.subheader(f"🇹🇼 台股 ({len(tw_stocks)})")
                if not tw_stocks:
                    st.caption("無符合條件之標的")
                for res in tw_stocks:
                    render_stock_card(res)
                    
            with col_jp:
                st.subheader(f"🇯🇵 日股 ({len(jp_stocks)})")
                if not jp_stocks:
                    st.caption("無符合條件之標的")
                for res in jp_stocks:
                    render_stock_card(res)

if __name__ == "__main__":
    main()
