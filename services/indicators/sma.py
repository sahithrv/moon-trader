
def sma_naive(values, window):
    result = []
    for i in range(len(values)):
        if i + 1 < window:
            result.append(None)
        else:
            window_values = values[i - window + 1: i + 1]
            result.append(sum(window_values) / window)

def sma(values, window):
    result = []
    window_sum = 0.0

    for i in range(len(values)):
        window_sum += values[i]

        if i >= window:
            window_sum -= values[i - window]

        if i + 1 < window:
            result.append(None)
        else:
            result.append(window_sum / window)

    return result    
