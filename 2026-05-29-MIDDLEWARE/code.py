# Created on: 2026-05-29

import random
import string
import time
from collections import defaultdict
from typing import DefaultDict

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


app = FastAPI()


@app.middleware("http")
async def add_request_id(request: Request, call_next):
	response = await call_next(request)
	request_id = "".join(random.choices(string.ascii_letters + string.digits, k=10))
	print(f"request_id={request_id}")
	response.headers["X-Request-ID"] = request_id
	return response


async def log_message(message: str) -> None:
	print(message)


class AdvancedMiddleware(BaseHTTPMiddleware):
	def __init__(self, app: FastAPI) -> None:
		super().__init__(app)
		self.rate_limit_records: DefaultDict[str, float] = defaultdict(float)

	async def dispatch(self, request: Request, call_next) -> Response:
		client = request.client
		client_ip = client.host if client else "unknown"
		current_time = time.time()

		last_time = self.rate_limit_records[client_ip]
		if current_time - last_time < 1:
			return JSONResponse(
				status_code=429,
				content={"detail": "Rate limit exceeded"},
			)

		self.rate_limit_records[client_ip] = current_time

		path = request.url.path
		await log_message(f"request_to={path}")

		start_time = time.time()
		response = await call_next(request)
		process_time = time.time() - start_time

		response.headers["X-Process-Time"] = f"{process_time:.6f}"
		await log_message(f"process_time={process_time:.6f}s")

		return response


app.add_middleware(AdvancedMiddleware)


@app.get("/")
async def root() -> dict:
	return {"message": "Hello world"}


@app.get("/say-hi")
async def say_hi() -> dict:
	return {"message": "Hello YouTube"}

