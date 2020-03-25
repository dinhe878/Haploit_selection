FROM debian:latest
MAINTAINER Ding He <dinghe6723@gmail.com>

# Download and install the latest SLiM from github
RUN aptitude install cmake && \
    git clone https://github.com/MesserLab/SLiM.git && \
    mkdir SLiM_build && \
    cd SLiM_build && \
    cmake -DCMAKE_BUILD_TYPE=Release ../SLiM && \
    make
