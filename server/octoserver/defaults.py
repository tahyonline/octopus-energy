from datetime import datetime, timezone

# Pyramid related
SRV_LISTEN_ADDRESS = 'localhost'
SRV_LISTEN_PORT = 6543
SPA_PATH = '../../spa/build'

# Octopus Energy related
TIME_DELTA = 90  # number of days to download in one call
LOCAL_TIMEZONE = datetime.now(timezone.utc).astimezone().tzinfo
