def ema(values, window):
    result = []

    if len(values) == 0:
        return result
    
    multiplier = 2 / (window + 1)
    previous_ema = None

    for i, value in enumerate(values):
        if i + 1 < window:
            result.append(None)
            continue

        if i + 1 == window:
            previous_ema = sum(values[0:window]) / window
            result.append(None)
            continue

        curr_ema = (value - previous_ema) * multiplier + previous_ema
        result.append(curr_ema)
        previous_ema = curr_ema
    
    return result