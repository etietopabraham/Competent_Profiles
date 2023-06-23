from setuptools import find_packages, setup
from typing import List

HYPHEN_E_DOT = "-e ."

def get_requirements(file_path:str)->List[str]:
    '''
        This function returns list of requirements
    '''
    with open(file_path, 'r') as file:
        requirements = [line.strip() for line in file if line.strip() != HYPHEN_E_DOT]

    return requirements


setup(
    name='CompetentProfiles',
    version='0.1.0',
    author='Etietop Abraham',
    author_email='etietopdemasabraham@gmail.com',
    packages=find_packages(),
    install_requires=get_requirements('requirements.txt'),
)