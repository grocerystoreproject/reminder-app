name: Build ReminderApp APK

on:
  push:
    branches:
      - main
  workflow_dispatch:

jobs:
  build-apk:
    runs-on: ubuntu-22.04

    steps:
      - name: Checkout Repository
        uses: actions/checkout@v3

      - name: Setup Python 3.10
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install System Dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y \
            openjdk-17-jdk \
            build-essential \
            git \
            zip \
            unzip \
            autoconf \
            libtool \
            pkg-config \
            zlib1g-dev \
            libssl-dev \
            libffi-dev \
            libltdl-dev \
            ccache

      - name: Setup Java
        run: |
          echo "JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64" >> $GITHUB_ENV

      - name: Upgrade pip
        run: |
          python -m pip install --upgrade pip setuptools wheel

      - name: Install Buildozer
        run: |
          pip install --upgrade cython==0.29.36
          pip install --upgrade buildozer==1.5.0

      - name: Build APK
        run: |
          export USE_CCACHE=1
          export GRADLE_OPTS="-Dorg.gradle.jvmargs=-Xmx2048m"
          yes | buildozer android debug
          
      - name: Upload APK
        uses: actions/upload-artifact@v4
        with:
          name: ReminderApp-APK
          path: bin/*.apk
