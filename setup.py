from setuptools import setup

setup(
    name="nextcord",
    author="vcoktlfre & tag-epic",
    url="https://github.com/nextcord/nextcord-v3",
    project_urls={"Issue Tracker": "https://github.com/nextcord/nextcord-v3"},
    packages=[],
    license="MIT",
    description="A fast, modular Discord API wrapper",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    install_requires=["aiohttp>=3.6.0,<4.0.0"],
    extras_require={
        "speed": ["orjson>=3.5.4", "aiodns>=1.1", "Brotli", "cchardet"],
        "dev": ["pytest", "black", "isort"],
    },
    python_requires=">=3.9.0",
    clasifiers=[
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Framework :: AsyncIO",
        "Framework :: aiohttp",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
)
