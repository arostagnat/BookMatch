# BookMatch
Book recommendation algorithm based on movie preferences

## Initialization
Add a folder named "raw_data" where you'll store the data to work with. This folder will be ignored by git
mkdir raw_data

### If your python version is different from 3.10
# pyenv install 3.10.6

### Create a virtualenv for the project
pyenv virtualenv 3.10.6 BookMatch_env

### Activate the virtualenv when you are located in the folder
pyenv local BookMatch_env

### Install the requirements.txt file
pip install -e .
