"""GnarlyClimber development configuration."""

import os

# Root of this application, useful if it doesn't occupy an entire domain
APPLICATION_ROOT = '/'

# Database file is var/route_heights.sqlite3
DATABASE_FILENAME = os.path.join(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
    'var', 'route_heights.sqlite3'
)

LIMIT_MTN_PROJECT_API_HIT_RATE = True
MIN_MTN_PROJECT_API_HIT_COOLDOWN = 3.0 #ignored if LIMIT_MTN_PROJECT_API_HIT_RATE is True

LIMIT_MTN_PROJECT_SCRAPE_RATE = True
MIN_MTN_PROJECT_SCRAPE_COOLDOWN = .34 #ignored if LIMIT_MTN_PROJECT_SCRAPE_RATE is True