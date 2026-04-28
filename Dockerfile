FROM --platform=linux/amd64 ubuntu:16.04

# Install basic dependencies and add Mahimahi PPA
RUN apt-get update && \
    apt-get install -y software-properties-common apt-transport-https ca-certificates wget curl && \
    add-apt-repository -y ppa:keithw/mahimahi && \
    apt-get update

# Install required apt packages
RUN apt-get install -y \
    sudo \
    mahimahi \
    apache2 \
    python-setuptools python-pip \
    xvfb xserver-xephyr tightvncserver unzip \
    python-dev \
    python-h5py python-scipy python-matplotlib \
    chromium-browser chromium-chromedriver \
    && rm -rf /var/lib/apt/lists/*

# Install pip for Python 2.7
RUN curl -O https://bootstrap.pypa.io/pip/2.7/get-pip.py && python get-pip.py && rm get-pip.py

# Install Selenium from source as specified in setup.py
RUN wget "https://pypi.python.org/packages/source/s/selenium/selenium-2.39.0.tar.gz" && \
    tar xvzf selenium-2.39.0.tar.gz && \
    cd selenium-2.39.0 && \
    python setup.py install && \
    cd .. && rm -rf selenium-2.39.0*
RUN sh -c "echo 'DBUS_SESSION_BUS_ADDRESS=/dev/null' > /etc/init.d/selenium"

# Install python dependencies for reinforcement learning
# TF 1.1.0 and TFLearn 0.3.1 per README.md
RUN pip install pyvirtualdisplay tensorflow==1.1.0 tflearn==0.3.1

# Setup Apache Server
WORKDIR /var/www/html
COPY video_server/myindex_*.html ./
COPY video_server/dash.all.min.js ./
COPY video_server/video* ./
COPY video_server/Manifest.mpd ./

# Create a non-root user for Mahimahi (fails as root)
RUN useradd -m -s /bin/bash pensieve && \
    echo "pensieve:pensieve" | chpasswd && \
    adduser pensieve sudo && \
    echo "pensieve ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

WORKDIR /workspace

# Create required output directories
RUN mkdir -p /workspace/cooked_traces \
    /workspace/rl_server/results \
    /workspace/run_exp/results \
    /workspace/real_exp/results

# Copy the rest of the project files
COPY . /workspace
RUN chown -R pensieve:pensieve /workspace

# Set default user to pensieve for Mahimahi
USER pensieve

# Start apache server and bash when container starts
CMD sudo service apache2 start && /bin/bash
