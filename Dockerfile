# Using image
FROM jupyter/nbviewer

USER root 

RUN pip3 install scs-sdk
EXPOSE 5050

ADD . /srv/nbviewer/
RUN invoke less


CMD ["python3", "-m", "nbviewer", "--port=5050" ,"--use_sae_storage"]
