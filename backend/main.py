from quart import current_app, request
from app import create_app


app = create_app()


@app.before_request
async def before_request():
    current_app.logger.info(f"Request received: {request.method} {request.path}")


@app.before_serving
async def before_serving():
    current_app.logger.info("Server starting")


@app.after_serving
async def after_serving():
    current_app.logger.info("Server shutting down")
