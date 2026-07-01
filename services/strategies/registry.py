from .ema_rsi_volume import EmaRsiVolumeStrategy

STRATEGIES = {
    "ema_rsi_volume_v1": EmaRsiVolumeStrategy(),
}

def get_strategy(name):
    if name not in STRATEGIES:
        raise ValueError(f"Unkown strategy: {name}")
    return STRATEGIES[name]
