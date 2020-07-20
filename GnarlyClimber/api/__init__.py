from GnarlyClimber.api.routes import get_routes
from GnarlyClimber.api.mtn_project_height_scraper import *

#global rate limiter
MTN_PROJECT_API_RATE_LIMITER = RateLimiter(GnarlyClimber.app.config['MIN_MTN_PROJECT_API_HIT_COOLDOWN'])
MTN_PROJECT_SCRAPE_RATE_LIMITER = RateLimiter(GnarlyClimber.app.config['MIN_MTN_PROJECT_SCRAPE_COOLDOWN'])
