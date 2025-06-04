from setuptools import setup, find_packages

setup(
    name="abm-lead-gen",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "gspread>=5.12.0",
        "oauth2client>=4.1.3",
        "gradio>=4.0.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "smolagents>=1.0.0"
    ],
    python_requires=">=3.8",
) 