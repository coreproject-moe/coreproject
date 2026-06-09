"""Quart app factory with geo initialization and Redis lifecycle."""

from quart import Quart
from quart_cors import cors

try:
    from flask_orjson import OrjsonProvider  # type: ignore[import]

    HAS_FLASK_ORJSON = True
except ImportError:
    HAS_FLASK_ORJSON = False

from coreproject_tracker.envs import BLOCKLIST_PATH, REDIS_URI
from coreproject_tracker.servers import http_blueprint, ws_blueprint
from coreproject_tracker.validators import _load_blocklist


def create_quart_app() -> Quart:
    """Build and configure the Quart application.

    Sets up CORS, optional orjson provider, blocklist loading,
    Redis lifecycle hooks, and registers HTTP/WebSocket blueprints.
    """
    app = Quart(__name__)
    app = cors(app, allow_origin="*")

    if HAS_FLASK_ORJSON:
        app.json = OrjsonProvider(app)  # type: ignore

    if BLOCKLIST_PATH:
        _load_blocklist(BLOCKLIST_PATH)

    from coreproject_tracker.singletons.redis import RedisHandler

    redis_manager = RedisHandler(REDIS_URI)

    @app.before_serving
    async def initialize_redis_connection():
        """Connect to Redis before the server starts accepting requests."""
        await redis_manager.init_redis()

    @app.after_serving
    async def close_redis_connection():
        """Close Redis connection when the server shuts down."""
        await redis_manager.close_redis()

    app.register_blueprint(http_blueprint)
    app.register_blueprint(ws_blueprint)

    return app
