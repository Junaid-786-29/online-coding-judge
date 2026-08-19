import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.logging_config import setup_logging
from app.routes.problems import router as problems_router
from app.routes.auth import router as auth_router
from app.routes.test_cases import router as test_cases_router
from app.routes.submissions import router as submissions_router

from app.exceptions.problem import ProblemNotFoundError
from app.exceptions.test_case import TestCaseNotFoundError
from app.exceptions.submission import (
    SubmissionNotFoundError,
    SubmissionAccessDeniedError,
)
from app.exceptions.user import UserNotFoundError

logger = setup_logging()
settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description=(
        "Production-ready Online Coding Judge API built with FastAPI, SQLAlchemy, MSSQL, "
        "JWT authentication, Repository Pattern, and isolated code execution."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response


@app.get(
    "/health",
    tags=["System"],
    summary="Health check",
    description="Lightweight health check endpoint for monitoring system availability.",
)
async def health_check():
    return {
        "status": "ok",
        "environment": settings.app_env,
    }


@app.exception_handler(ProblemNotFoundError)
async def problem_not_found_handler(
    request: Request,
    exc: ProblemNotFoundError
):
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Problem Not Found"
        }
    )


@app.exception_handler(TestCaseNotFoundError)
async def test_case_not_found_handler(
    request: Request,
    exc: TestCaseNotFoundError
):
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Test Case Not Found"
        }
    )


@app.exception_handler(SubmissionNotFoundError)
async def submission_not_found_handler(
    request: Request,
    exc: SubmissionNotFoundError
):
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Submission Not Found"
        }
    )


@app.exception_handler(SubmissionAccessDeniedError)
async def submission_access_denied_handler(
    request: Request,
    exc: SubmissionAccessDeniedError
):
    return JSONResponse(
        status_code=403,
        content={
            "detail": str(exc)
        }
    )


@app.exception_handler(UserNotFoundError)
async def user_not_found_handler(
    request: Request,
    exc: UserNotFoundError
):
    return JSONResponse(
        status_code=404,
        content={
            "detail": "User Not Found"
        }
    )


@app.exception_handler(ValueError)
async def value_error_handler(
    request: Request,
    exc: ValueError
):
    return JSONResponse(
        status_code=400,
        content={
            "detail": str(exc)
        }
    )


@app.exception_handler(Exception)
async def global_unexpected_exception_handler(
    request: Request,
    exc: Exception
):
    """
    Catch-all 500 handler for unexpected server errors.
    Logs full exception traceback server-side and returns a generic safe message.
    Never leaks sensitive details, stack traces, or connection strings.
    """
    logger.exception(f"Unhandled server error on {request.method} {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error."
        }
    )


app.include_router(problems_router)
app.include_router(auth_router)
app.include_router(test_cases_router)
app.include_router(submissions_router)