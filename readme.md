<p align="center">
   <a href="https://www.codefactor.io/repository/github/inejka/crawlviewer"><img src="https://www.codefactor.io/repository/github/inejka/crawlviewer/badge" alt="CodeFactor" /></a>
   <a href="https://codecov.io/gh/Inejka/crawlviewer" > 
   <img src="https://codecov.io/gh/Inejka/crawlviewer/branch/main/graph/badge.svg?token=EZJG8ZB0IS"/> 
   </a>
</p>

# About
The main purpose of this project is to give you a simple app to save a bunch of sites on your hard drive and then view them easily. Maybe later I will add the ability to start crawlers from this app. 

# Currently supported crawlers
 - [nudecrawler](https://github.com/yaroslaff/nudecrawler)
 
# Installation

## Requirements
- python
- npm 
   - [link](https://nodejs.org/en/download) to download windows installer
   - on linux install it with your package manager like this

         sudo apt install npm         
- wget
   - on windows easiest way is to install [choco](https://chocolatey.org/install) and then run
            
         choco install wget 
   - on linux install it with your package manager like this

         sudo apt install wget      

## Windows
```bat
git clone https://github.com/Inejka/crawlviewer
cd crawlviewer
python -m venv .\server\env
.\server\env\Scripts\activate
pip install -r .\server\requirements.txt
cd client
npm install
```
## Linux
```sh
git clone https://github.com/Inejka/crawlviewer
cd crawlviewer
python -m venv ./server/env
source server/env/bin/activate
pip install -r server/requirements.txt
cd client
npm install
```
# Run
- windows
      
      just run run.bat

- linux

      chmod +x run.sh
      ./run.sh

  Then visit [http://localhost:5173/](http://localhost:5173/)
