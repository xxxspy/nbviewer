# Using thebuntu image
FROM jupyter/nbviewer

MAINTAINER Project Jupyter <jupyter@googlegroups.com>
EXPOSE 5050
CMD ["python3", "-m", "nbviewer", "--port=5050"]
