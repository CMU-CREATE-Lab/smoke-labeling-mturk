# smoke-labeling-mturk
Smoke labeling experiment for Amazon Mechanical Turk.

### Task 1: Tutorial
- Title:
  - Interactive Tutorial for Labeling Industrial Smoke Emissions
- Description:
  - This tutorial provides guidelines about how to recognize industrial smoke emissions. This tutorial is the qualification of a follow-up task of labeling smoke emissions ([provide task link or id]).
- URL:
  - https://cmu-create-lab.github.io/smoke-labeling-mturk/tutorial.html

### Task 2: Smoke Labeling
- Title:
  - Industrial Smoke Emission Labeling
- Description:
  - This task asks participants to identify industrial smoke emissions from a collection of videos. This task needs the qualification of completing a tutorial ([provide task link or id]).
- URL:
  - https://cmu-create-lab.github.io/smoke-labeling-mturk/label.html?batch_id=0
- Note:
  - There are 60 batches (from batch_id=0 to batch_id=59).
  
# Setup this tool
Install conda. This assumes that Ubuntu is installed. A detailed documentation is [here](https://conda.io/projects/conda/en/latest/user-guide/install/index.html). First visit [here](https://conda.io/miniconda.html) to obtain the downloading path. The following script install conda for all users:
```sh
wget https://repo.continuum.io/miniconda/Miniconda3-4.7.12.1-Linux-x86_64.sh
sudo sh Miniconda3-4.7.12.1-Linux-x86_64.sh -b -p /opt/miniconda3

sudo vim /etc/bash.bashrc
# Add the following lines to this file
export PATH="/opt/miniconda3/bin:$PATH"
. /opt/miniconda3/etc/profile.d/conda.sh

source /etc/bash.bashrc
```
For Mac OS, I recommend installing conda by using [Homebrew](https://brew.sh/).
```sh
brew cask install miniconda
echo 'export PATH="/usr/local/Caskroom/miniconda/base/bin:$PATH"' >> ~/.bash_profile
echo '. /usr/local/Caskroom/miniconda/base/etc/profile.d/conda.sh' >> ~/.bash_profile
source ~/.bash_profile
```
Create conda environment and install packages. It is important to install pip first inside the newly created conda environment.
```sh
conda create -n smoke-labeling-mturk
conda activate smoke-labeling-mturk
conda install python=3.7
conda install pip
which pip # make sure this is the pip inside the deep-smoke-machine environment
sh smoke-labeling-mturk/install_packages.sh
```
If the environment already exists and you want to remove it before installing packages, use the following:
```sh
conda env remove -n smoke-labeling-mturk
```
