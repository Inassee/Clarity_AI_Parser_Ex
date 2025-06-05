from setuptools import setup, find_packages
setup(
    name="clarity_log_parser",
    version="0.1.0",
    packages=find_packages(include=["clarity_parser", "clarity_parser.*"]),
    install_requires=["pytest>=7.0"],
    entry_points={
        "console_scripts": [
            "log-parse=clarity_parser.static_parser:parse_file",
            "log-stream=clarity_parser.streaming_parser:main",
        ]
    },
)
