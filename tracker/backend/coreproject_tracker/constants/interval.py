from datetime import timedelta

ANNOUNCE_INTERVAL = int(timedelta(minutes=10).total_seconds())
ANNOUNCE_INTERVAL_MIN = int(timedelta(minutes=30).total_seconds())
ANNOUNCE_INTERVAL_MAX = int(timedelta(hours=1).total_seconds())
WEBSOCKET_INTERVAL = int(timedelta(minutes=2).total_seconds())