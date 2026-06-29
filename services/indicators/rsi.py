# RSI

def rsi(closes, window=14):
    result = [None] * len(closes)

    gains = []
    losses = []

    for i in range(1, len(closes)):
        change = closes[i] - closes[i - 1]
        gains.append(max(change, 0))
        losses.append(max(-change, 0))
    
    gain_sum = 0.0
    loss_sum = 0.0

    for i in range(len(gains)):
        gain_sum += gains[i]
        loss_sum += losses[i]

        if i >= window:
            avg_gain = gain_sum / window
            avg_loss = loss_sum / window

            close_index = i + 1

            if avg_loss == 0:
                result[close_index] = 100.0
            else:
                rs = avg_gain / avg_loss
                result[close_index] = 100 - (100 / (1 + rs))
    
    return result
        