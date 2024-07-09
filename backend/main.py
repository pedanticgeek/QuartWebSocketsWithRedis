from quart import current_app
from app import create_app


app = create_app()


@app.before_serving
async def before_serving():
    current_app.logger.info("Server starting")


@app.after_serving
async def after_serving():
    current_app.logger.info("Server shutting down")
