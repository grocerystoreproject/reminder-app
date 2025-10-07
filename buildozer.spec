name: Build My Reminders APK

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build-apk:
    runs-on: ubuntu-20.04
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Python 3.9
        uses: actions/setup-python@v5
        with:
          python-version: '3.9'
      
      - name: Set up Java 11
        uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '11'
      
      - name: Install system dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y \
            build-essential \
            git \
            zip \
            unzip \
            libssl-dev \
            libffi-dev \
            python3-dev \
            autoconf \
            automake \
            libtool \
            pkg-config \
            zlib1g-dev \
            libncurses5-dev \
            cmake
      
      - name: Install Python dependencies
        run: |
          pip install --upgrade pip
          pip install --upgrade setuptools wheel
          pip install buildozer==1.4.0
          pip install cython==0.29.33
      
      - name: Cache Buildozer directories
        uses: actions/cache@v4
        with:
          path: |
            .buildozer
          key: buildozer-ubuntu20-${{ hashFiles('buildozer.spec') }}
          restore-keys: |
            buildozer-ubuntu20-
      
      - name: Build APK with Buildozer
        run: |
          yes | buildozer -v android debug
      
      - name: Upload APK artifact
        uses: actions/upload-artifact@v4
        with:
          name: MyReminders-v2.5
          path: bin/*.apk
          retention-days: 30
          if-no-files-found: error
