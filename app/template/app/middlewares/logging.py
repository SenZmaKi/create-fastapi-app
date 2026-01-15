import time
import json
from starlette.types import ASGIApp, Receive, Scope, Send, Message
from app.utils.logger import logger


class LoggingMiddlewareASGI:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        # Only log HTTP requests
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start_time = time.time()

        # Extract client info safely
        client = scope.get("client")
        client_str = f"{client[0]}:{client[1]}" if client else "N/A"

        # Extract headers
        headers = {k.decode(): v.decode() for k, v in scope.get("headers", [])}
        # Filter sensitive headers
        filtered_headers = {
            k: v
            for k, v in headers.items()
            if k.lower() not in ["authorization", "cookie"]
        }

        # Capture request body
        body_bytes = b""

        async def receive_wrapper():
            nonlocal body_bytes
            message = await receive()
            if message["type"] == "http.request":
                body_bytes += message.get("body", b"")
            return message

        # Log request received with headers
        log_data = {
            "method": scope["method"],
            "path": scope["path"],
            "client": client_str,
            "headers": filtered_headers,
        }

        logger.info("Request received", extra=log_data)

        # We need to capture the response to log status_code and duration
        # Wrap the send callable to intercept the response
        response_status = None
        response_body = b""

        async def send_wrapper(message: Message):
            nonlocal response_status, response_body
            if message["type"] == "http.response.start":
                response_status = message["status"]
            elif message["type"] == "http.response.body":
                response_body += message.get("body", b"")
            await send(message)

        try:
            await self.app(scope, receive_wrapper, send_wrapper)

            # Log request body for non-GET requests
            if scope["method"] != "GET" and body_bytes:
                try:
                    body_str = body_bytes.decode("utf-8")
                    # Try to parse as JSON for better formatting
                    try:
                        body_json = json.loads(body_str)
                        log_data["body"] = body_json
                    except json.JSONDecodeError:
                        log_data["body"] = body_str[:1000]  # Limit body size
                except UnicodeDecodeError:
                    log_data["body"] = "<binary data>"

            process_time = time.time() - start_time

            response_log = {
                "method": scope["method"],
                "path": scope["path"],
                "status_code": response_status,
                "process_time": f"{process_time:.4f}s",
            }

            # Log response body for all responses, but skip if larger than 5MB
            max_body_size = 5 * 1024 * 1024  # 5 MB in bytes
            if response_body and len(response_body) <= max_body_size:
                try:
                    response_str = response_body.decode("utf-8")
                    try:
                        response_json = json.loads(response_str)
                        response_log["response_body"] = response_json
                    except json.JSONDecodeError:
                        response_log["response_body"] = response_str[:1000]
                except UnicodeDecodeError:
                    response_log["response_body"] = "<binary data>"
            elif response_body and len(response_body) > max_body_size:
                response_log["response_body"] = (
                    f"<body too large: {len(response_body)} bytes>"
                )

            if response_status and response_status >= 400:
                logger.warning("Request processed with error", extra=response_log)
            else:
                logger.info("Request processed", extra=response_log)

        except Exception as e:
            process_time = time.time() - start_time
            logger.exception(
                "Exception during request processing",
                exc_info=e,
                extra={
                    "method": scope["method"],
                    "path": scope["path"],
                    "process_time": f"{process_time:.4f}s",
                    "exception_type": type(e).__name__,
                },
            )
            raise


def add_logging_middleware(app):
    app.add_middleware(LoggingMiddlewareASGI)
