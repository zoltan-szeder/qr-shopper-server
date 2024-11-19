from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse


class ExceptionHandler:
    def handle_exception(self, request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.status_code,
                "errors": {
                    "location": request.url.path,
                    "message": exc.detail
                },
                "message": exc.detail
            }
        )
