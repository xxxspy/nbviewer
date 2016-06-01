# Using thebuntu image
FROM jupyter/nbviewer

MAINTAINER Project Jupyter <jupyter@googlegroups.com>
USER root
RUN pip3 install scs-sdk
EXPOSE 5050
WORKDIR /srv/nbviewer
# build css
ADD . /srv/nbviewer/
RUN invoke less


CMD ["python3", "-m", "nbviewer", "--port=5050" ,"--use_sae_storage","--no_cache"]
