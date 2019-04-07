echo "Installing python-dev"
sudo apt-get install python3-dev

echo "installing virtualenv deps"
pip install --upgrade pip virtualenv setuptools

echo "Creating kivy virtual environment"
virtualenv --no-site-packages -p /usr/bin/python3 vadix_airscan

echo "Entering kivy virtual environment"
source vadix_airscan/bin/activate

echo "Installing Cython"
pip install cython==0.25.2 

echo "Installing Kivy"
pip install kivy pygame buildozer
