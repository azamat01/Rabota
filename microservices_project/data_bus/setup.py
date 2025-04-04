from setuptools import setup, find_packages

setup(
    name="data_bus",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        # Добавьте сюда все необходимые зависимости для этого микросервиса
        "requests",  # Например, добавьте requests, если он используется
        "flask",     # Пример для Flask
    ],
)
