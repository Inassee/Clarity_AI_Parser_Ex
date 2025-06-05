from setuptools import setup, find_packages

setup(
    name="clarity_log_parser",
    version="0.1.0",
    packages=find_packages(include=["clarity_parser", "clarity_parser.*"]),
    install_requires=[
        "pandas>=2.0",
        "python-dateutil>=2.8",
    ],
    entry_points={
        "console_scripts": [
            "log-parse=clarity_parser.log_parser_all_in_one:parse_logs",
        ]
    },
)
