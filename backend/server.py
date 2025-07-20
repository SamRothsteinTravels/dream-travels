from enhanced_server import *
from theme_park_routes import theme_park_router

# Add theme park routes
app.include_router(theme_park_router)