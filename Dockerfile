FROM ubuntu:latest
MAINTAINER Ding He <dinghe6723@gmail.com>

# Download and install git and the latest SLiM from github
RUN apt update -y && \
    apt upgrade -y && \
    apt install git -y && \
    git clone https://github.com/MesserLab/SLiM.git && \
    mkdir SLiM_build && \
    cd SLiM_build && \
    cmake -DCMAKE_BUILD_TYPE=Release ../SLiM && \
    make
