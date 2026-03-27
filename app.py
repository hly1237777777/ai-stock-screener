import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime

# --- 頁面配置：手機端建議使用 centered 佈局 ---
st.set_page_config(page_title="AI 量化指揮中心", layout="centered")

# 股票名稱映射表 (已新增 LLY, BA, TTD)
NAME_MAP = {
    # 台股
    "3711.TW": "日月光投控", "2059.TW": "川湖", "2308.TW": "台達電", 
    "2330.TW": "台積電", "2454.TW": "聯發科", "2317.TW": "鴻海", 
    "3231.TW": "緯創", "2327.TW": "國巨", "2458.TW": "義隆", 
    "6176.TW": "瑞儀", "1708.TW": "東鹼", "2404.TW": "漢唐", 
    "6239.TW": "力成", "3037.TW": "欣興", "2408.TW": "南亞科", "3491.TW": "昇達科",
    # 日股
    "7733.T": "奧林巴斯", "1540.T": "純金信託", "9432.T": "日本電信電話", 
    "8058.T": "三菱商事", "6501.T": "日立製作所", "4063.T": "信越化學", 
    "1542.T": "純銀信託", "6857.T": "愛德萬測試", "7011.T": "三菱重工", 
    "2644.T": "日股半導體ETF", "8001.T": "伊藤忠商事", "7203.T": "豐田汽車", 
    "7974.T": "任天堂", "1699.T": "野村原油ETF", "1321.T": "日經225ETF",
    # 美股與 ETF (包含最新加入的標的)
    "LLY": "禮來", "BA": "波音", "TTD": "The Trade Desk",
    "NVDA": "輝達", "MRVL": "邁威爾科技", "COHR": "科希倫", "GOOGL": "谷歌", 
    "PLUG": "普拉格能源", "NBIS": "Nebius Group", "URNM": "Sprott鈾礦ETF", 
    "PYPL": "PayPal", "MU": "美光科技", "ETN": "伊頓科技", "POW": "日昇新能",
    "LMT": "洛克希德馬丁", "NOC": "諾格", "GLW": "康寧", "GEV": "GE Vernova", 
    "VRT": "維諦技術", "PLTR": "帕蘭提爾", "RKLB": "火箭實驗室", "AAOI": "應用光電", 
    "TNDM": "Tandem醫療", "DAC": "德納斯", "ONDS": "昂達斯", "TSM": "台積電ADR", 
    "AAPL": "蘋果", "MSFT": "微軟", "SPY": "標普500ETF",
    "SOFI": "SoFi科技", "DIS": "迪士尼", "BIDU": "百度", 
    "XOP": "標普油氣開採ETF", "VDE": "先鋒能源ETF", "XLE": "能源板塊SPDR",
    "DOG": "道指反向ETF", "PSQ": "納指反向ETF",
    "SGOL": "abrdn實體黃金ETF", "UGL": "2倍做多黃金ETF"
}

class TacticalScanner:
    def __init__(self, symbols):
        self.symbols = symbols

    def get_tradingview_link(self, symbol):
        """生成 TradingView 連結 (支援跨市場轉換)"""
        tv_symbol = symbol
        if ".TW" in symbol:
            tv_symbol = f"TWSE:{symbol.replace('.TW', '')}"
        elif ".T" in symbol:
            tv_symbol = f"TSE:{symbol.replace('.T', '')}"
        elif "-USD" in symbol:
            tv_symbol = f"BINANCE:{symbol.replace('-USD', 'USDT')}"
        return f"https://www.tradingview.com/chart/?symbol={tv_symbol}"

    def fetch_data(self, symbol):
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="6mo")
            return df if not df.empty and len(df) >= 50 else None
        except:
            return None

    def calculate_indicators(self, df):
        last_close = float(df['Close'].iloc[-1])
        
        # 均線
        ema20 = df['Close'].ewm(span=20, adjust=False).mean()
        ema50 = df['Close'].ewm(span=50, adjust=False).mean()
        
        # MACD (12, 26, 9)
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        hist = macd - signal
        
        # KD (9, 3)
        low_min = df['Low'].rolling(window=9).min()
        high_max = df['High'].rolling(window=9).max()
        k = 100 * (df['Close'] - low_min) / (high_max - low_min)
        d = k.rolling(window=3).mean()
        
        # CCI (14)
        tp = (df['High'] + df['Low'] + df['Close']) / 3
        cci = (tp - tp.rolling(14).mean()) / (0.015 * tp.rolling(14).std())
        
        # Bias (20EMA)
        bias_20 = float((last_close - ema20.iloc[-1]) / ema20.iloc[-1] * 100)
        
        # 統一輸出，並使用 float() 確保資料純粹性
        return {
            "Close": last_close, 
            "EMA20": float(ema20.iloc[-1]), 
            "EMA50": float(ema50.iloc[-1]),
            "Hist": float(hist.iloc[-1]), 
            "K": float(k.iloc[-1]), 
            "D": float(d.iloc[-1]), 
            "CCI": float(cci.iloc[-1]),
            "Bias_20": bias_20
        }

    def generate_detailed_reason(self, last):
        close = last['Close']
        if close > last['EMA20'] and last['Hist'] > 0 and 0 < last['Bias_20'] < 5:
            return "ADD-ON", f"🔥 趨勢向上：站穩 20EMA，乖離率僅 {last['Bias_20']:.2f}%，MACD 柱體持續擴張。"
        elif last['K'] < 30 and last['K'] > last['D'] and last['CCI'] > -100:
            return "EXECUTE", f"🎯 底部訊號：KD 低檔交叉(K={last['K']:.1f})，CCI 指標由超賣區反彈。"
        elif close < last['EMA50'] or (last['K'] > 80 and last['Hist'] < 0):
            if close < last['EMA50']:
                return "EVACUATE", f"⚠️ 趨勢破壞：跌破中期均線 50EMA，請注意回撤風險。"
            else:
                return "EVACUATE", f"⚠️ 技術背離：高檔超買但動能柱已萎縮。"
        return "WAIT", "⏳ 監控中：價格在盤整區間，指標暫無明顯偏向。"

# --- UI 介面 ---
st.title("🛡️ 全球量化戰術中心")
st.caption(f"數據最後更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

with st.sidebar:
    st.header("📋 股池配置")
    market_filter = st.multiselect("選擇市場", ["台股", "美股", "日股"], default=["美股", "台股", "日股"])
    run_scan = st.button("🚀 開始全量化掃描", use_container_width=True)

if run_scan:
    targets = []
    if "台股" in market_filter: targets.extend([k for k in NAME_MAP.keys() if ".TW" in k])
    if "美股" in market_filter: targets.extend([k for k in NAME_MAP.keys() if "." not in k])
    if "日股" in market_filter: targets.extend([k for k in NAME_MAP.keys() if ".T" in k])
    
    scanner = TacticalScanner(targets)
    results = []
    
    progress = st.progress(0)
    for i, sym in enumerate(targets):
        df = scanner.fetch_data(sym)
        if df is not None:
            last = scanner.calculate_indicators(df)
            zone, reason = scanner.generate_detailed_reason(last)
            results.append({
                "代號": sym, "名稱": NAME_MAP.get(sym, sym),
                "價格": f"{last['Close']:.2f}", "戰術": zone, "理由": reason,
                "TV連結": scanner.get_tradingview_link(sym)
            })
        progress.progress((i + 1) / len(targets))
    
    # 手機版優化佈局：整合圖表按鈕
    for z_type, z_name, z_color in [("ADD-ON", "🔥 加碼推背區", "blue"), ("EXECUTE", "🎯 進入打擊區", "green"), ("EVACUATE", "⚠️ 風險撤退區", "red")]:
        subset = [r for r in results if r['戰術'] == z_type]
        if subset:
            with st.expander(f"{z_name} ({len(subset)})", expanded=True):
                for item in subset:
                    cols = st.columns([3, 1]) 
                    with cols[0]:
                        st.write(f"**{item['代號']} {item['名稱']}** | 價格: {item['價格']}")
                        st.caption(item['理由'])
                    with cols[1]:
                        st.link_button("📊 圖表", item['TV連結'], use_container_width=True)
                    st.divider()
