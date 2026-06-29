from returns import daily_return


# Rolling Volatility
# First get thr daily return - then we compute the rolling standard deviation to get this.

def rolling_volatility(closes, window):
    returns = daily_return(closes)
    result = []

    for i in range(len(returns)):
        if i + 1 < window or returns[i] is None:
            result.append(None)
            continue
        
        window_returns = returns[i - window + 1 : i + 1]

        if any(r is None for r in window_returns):
            result.append(None)
            continue
        
        mean = sum(window_returns) / window
        variance = sum((r - mean) ** 2 for r in window_returns) / window
        result.append(variance ** 0.5)
    
    return result