from setuptools import find_packages, setup

setup(
    name="genetic_algorithms",
    version="0.0.1",
    packages=find_packages(),
    description="Package to develop Genetic Algorithms 2020 Fing.",
    author="TheDuo",
    install_requires=[
        "deap",
        "numpy",
        "black",
        "isort",
        "matplotlib",
        "tqdm",
        "pandas",
    ],
    python_requires=">=3.7,<4.0",
    include_package_data=True,
    entry_points="""
        [console_scripts]
        mtsp=scripts.main:main
    """,
)
