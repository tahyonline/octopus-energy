from datetime import datetime, timezone

# Logging related
LOGGING_FORMAT = 'APP %(asctime)s %(message)s'

# Pyramid related
SRV_LISTEN_ADDRESS = 'localhost'
SRV_LISTEN_PORT = 6543
SPA_PATH = '../../spa/build'

# Frontend related
DATE_TIME_FORMAT = "%a, %d %b %Y %H:%M %z"

# Octopus Energy related
TIME_DELTA = 90  # number of days to download in one call
LOCAL_TIMEZONE = datetime.now(timezone.utc).astimezone().tzinfo
CSV_FILE_LOCATION = ".."