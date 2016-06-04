# Using image
FROM jupyter/nbviewer

MAINTAINER Project Jupyter <jupyter@googlegroups.com>
USER root

#local
# Set the locale
RUN locale-gen en_US.UTF-8  
ENV LANG en_US.UTF-8  
ENV LANGUAGE en_US:en  
ENV LC_ALL en_US.UTF-8  

RUN pip3 install scs-sdk
EXPOSE 5050
WORKDIR /srv/nbviewer
# build css
ADD . /srv/nbviewer/
RUN invoke less


CMD ["python3", "-m", "nbviewer", "--port=5050" ,"--use_sae_storage"]
