# Volume Weighted Average Price
# typical_price = (high + low + close) / 3
# sum(typical_price * volume) / sum(volume)

def vwap(highs, lows, closes, volumes):
    result = []
    
    total_price_vol = 0.0
    total_vol = 0.0

    for i in range(len(closes)):
        typical_price = (highs[i] + lows[i] + closes[i]) / 3
        vol = volumes[i]

        total_price_vol += typical_price * vol
        total_vol += vol

        if total_vol == 0:
            result.append(None)
        else:
            result.append(total_price_vol / total_vol)
    
    return result

