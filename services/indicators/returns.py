def daily_return(closes):
    result = [None]

    for i in range(1, len(closes)):
        previous = closes[i - 1]
        current = closes[i]

        if previous == 0:
            result.append(None)
        else:
            result.append((current - previous) / previous)
    
    return result