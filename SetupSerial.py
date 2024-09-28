import sys
import pip

pip.main(['install', 'pyserial', '--user'])

packages_path = "C:\\Users\\daunt\\AppData\\Roaming\\Python\\Python39\\Scripts" + "\\..\\site-packages"
sys.path.insert(0, packages_path )