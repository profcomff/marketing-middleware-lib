from setuptools import find_packages, setup

setup(
    name="logger-middleware",
    version="0.1.1",
    packages=find_packages(),
    install_requires=["fastapi", "starlette", "httpx", "auth-lib-profcomff[fastapi]"],
    author="DROPDATABASE",
    description="Middleware для логирования запросов в FastAPI",
    python_requires=">=3.7",
)
