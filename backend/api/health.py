from quart import Blueprint, current_app
from quart_redis import get_redis
from version import VERSION

health_bp = Blueprint("health", __name__)


@health_bp.route(f"/api/{VERSION}/health")
async def health_check():
    try:
        redis = get_redis()
        await redis.ping()
        return {"status": "healthy", "redis": "connected"}, 200
    except Exception as e:
        current_app.logger.error(f"Health check failed: {str(e)}")
        return {"status": "unhealthy", "redis": "disconnected"}, 503
