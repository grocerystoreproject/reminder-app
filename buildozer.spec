name: Build APK

on:
  push:
    branches:
      - main
  pull_request:

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout repository
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.10'

    - name: Install system dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y \
          python3-pip \
          python3-venv \
          openjdk-17-jdk \
          wget \
          unzip \
          build-essential \
          git \
          zip \
          libncurses5 \
          libncursesw5 \
          libtinfo5 \
          zlib1g-dev \
          libssl-dev \
          libffi-dev

    - name: Create and activate virtual environment
      run: |
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip setuptools wheel

    - name: Install Buildozer and dependencies
      run: |
        source venv/bin/activate
        pip install --upgrade cython==0.29.36
        pip install --upgrade buildozer==1.5.0

    - name: Setup Android environment
      run: |
        mkdir -p ~/.buildozer/android/platform
        
    - name: Cache Buildozer global directory
      uses: actions/cache@v4
      with:
        path: ~/.buildozer
        key: buildozer-${{ hashFiles('buildozer.spec') }}

    - name: Cache Buildozer build directory
      uses: actions/cache@v4
      with:
        path: .buildozer
        key: buildozer-build-${{ hashFiles('**/*.py', 'buildozer.spec') }}

    - name: Build APK with Buildozer
      run: |
        source venv/bin/activate
        yes | buildozer android debug

    - name: Upload APK artifact
      uses: actions/upload-artifact@v4
      with:
        name: reminderapp-debug
        path: bin/*.apk
        if-no-files-found: error
