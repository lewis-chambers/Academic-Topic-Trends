import setuptools

with open("README.md", "r") as fh:

    long_description = fh.read()

with open ('requirements.txt', 'r') as fh:
    requirements = fh.read().splitlines()

setuptools.setup(

    name="paper_popularity",

    version="1.0.0",

    author="Lewis Chambers",

    author_email="lewis.n.chambers@gmail.com",

    description="Paper Popularity Plotter",

    url="https://github.com/lewis-chambers/paper_popularity_plotter",

    install_requires=requirements,

    packages=setuptools.find_packages(),

    python_requires='>=3',

)
