from setuptools import setup, find_packages

setup(
    name="logger-middleware",
    version="0.1.1",
    packages=find_packages(),
    install_requires=["fastapi", "starlette", "httpx", "auth-lib-profcomff[fastapi]"],
    author="Ukhanov AK",
    description="Middleware для логирования запросов в FastAPI",
    python_requires=">=3.7",
)