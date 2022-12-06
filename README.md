# Palo Alto Log Cruncher

## Introduction

pacrunch.py is a python application that can "crunch" Palo Alto traffic log files.

### Features

* Deduplicate rows by specifying a column that should be unique.
* Remove empty rows.
* Remove specific columns by their header name.
* Perform a reverse DNS lookup on IP addresses and add a new column with the results.
* Override the local host DNS server and specify your own.

## About This Release
This is the first official release and it may have some bugs.

## Installation

### Installing Python

You will be **required to install Python 3** if you don't currently have it. <br> 
Link: [Python3](https://www.python.org/), the latest version is recommended.

---

### Optional Setup
It is recommended that you install this application in a Python Virtual Environment, you can do that by navigating to the directoy containing pacrunch.py and typing the following command in the terminal (or powershell)
```shell
python3 -m venv ./venv
```
You can then launch the virtual environment with one of the following commands:

**Linux/macOS**
```shell
source ./venv/bin/activate
```

**Windows (PowerShell)**
```powershell
source .\venv\bin\activate.ps1
```

---

### Required Setup
You can use the requirement.txt to install the required modules
```shell
pip3 install -r requirements.txt
```

### Running pacrunch.py
First, make sure to review and edit the config.yml with your requirements.

Once you are happy with the configuration, you can run the program:
```shell
python3 pacrunch.py
```