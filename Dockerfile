FROM continuumio/anaconda3
MAINTAINER Keisuke Kiriyama

ADD files /files
ADD programs /programs
CMD python /programs/main.py
