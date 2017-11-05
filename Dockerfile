############################################################
# Dockerfile for the CSDMS software stack
############################################################

# Set the base image to ubuntu
FROM ubuntu

# File Author / Maintainer
MAINTAINER Eric Hutton

# Update the sources list
RUN apt-get update

# Install basic applications
RUN apt-get install -y --fix-missing \
  tar \
  git \
  curl \
  vim \
  build-essential

RUN useradd --create-home --shell /bin/bash csdms
RUN echo 'csdms:dragon' | chpasswd

USER csdms
WORKDIR /home/csdms

# Install Python and Basic Python Tools
RUN curl https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh > miniconda.sh
RUN /bin/bash ./miniconda.sh -b -f -p /home/csdms/python
ENV PATH=/home/csdms/python/bin:$PATH

RUN conda config --add channels conda-forge
RUN conda config --add channels csdms-stack
RUN conda clean --lock
RUN conda config --set always_yes yes --set changeps1 no
RUN conda install python=2.7
RUN conda install -q \
  conda-build \
  anaconda-client \
  scipy \
  matplotlib \
  ipython

RUN git clone https://github.com/landlab/landlab && \
  conda install --file=landlab/requirements.txt && \
  cd landlab && \
  python setup.py develop

RUN git clone https://github.com/mcflugen/overland_flow && \
  cd overland_flow && \
  python setup.py develop

CMD cd /home/csdms/landlab && git pull && python setup.py develop && \
  cd /home/csdms/overland_flow && git pull && python setup.py develop && \
  /bin/bash
