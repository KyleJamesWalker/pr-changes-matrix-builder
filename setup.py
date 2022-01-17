"""Package setup"""
from setuptools import find_packages, setup

requirements = [
    "yamlsettings<3",
]

extras_require = {
    "test": [
        "flake8<4",
        "flake8-docstrings==1.6.0",
        "pytest==6.2.5",
        "pytest-black==0.3.12",
        "pytest-flake8==1.0.7",
        "pytest-cov==3.0.0",
        "pytest-xdist==2.5.0",
        "pook==1.0.2",
    ],
    "dev": ["ipython", "debugpy"],
    "setup": [
        "bumpversion",
        "pytest-runner",
    ],
}

extras_require.update(all=sorted(set().union(*extras_require.values())))

setup(
    name="pr_changes",
    version="0.0.1",
    author="KyleJamesWalker",
    description="Build a matrix from a PR",
    packages=find_packages(),
    package_data={
        "": ["*.yaml"],
    },
    install_requires=requirements,
    extras_require=extras_require,
    setup_requires=extras_require["setup"],
    tests_require=extras_require["test"],
    test_suite="tests",
    entry_points={
        "console_scripts": [
            "pr_changes = pr_changes.__main__:main",
        ],
    },
)
