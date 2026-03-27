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
        data = stock_obj.history(period
