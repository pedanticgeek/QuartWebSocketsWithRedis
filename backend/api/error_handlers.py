class APIException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


async def handle_api_exception(e: APIException):
    response = {"error": e.message, "status": e.status_code, "ok": False}
    return response
