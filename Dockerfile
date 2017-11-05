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

# Install Python and Basic Python Tools
RUN curl https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh > miniconda.sh
RUN /bin/bash ./miniconda.sh -b -f -p /usr/local/python
ENV PATH=/usr/local/python/bin:$PATH

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

RUN useradd --create-home --shell /bin/bash csdms
RUN echo 'csdms:dragon' | chpasswd

USER csdms
WORKDIR /home/csdms

RUN git clone https://github.com/landlab/landlab && \
  cd landlab && \
  conda install --file=requirements.txt

RUN git clone https://github.com/mcflugen/overland_flow

CMD cd landlab && git pull && python setup.py develop
CMD cd overland_flow && git pull && python setup.py develop
