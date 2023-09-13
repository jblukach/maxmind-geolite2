### 2.95.1 (build ae455d8) ###
FROM 070176467818.dkr.ecr.us-west-2.amazonaws.com/getpublicip:latest AS layer
FROM public.ecr.aws/lambda/python:latest
RUN yum -y update && yum clean all
### layer code ###
WORKDIR /opt
COPY --from=layer /opt/ .
### function code ###
WORKDIR /var/task
COPY download.py requirements.txt ./
RUN pip --no-cache-dir install -r requirements.txt --upgrade
CMD ["download.handler"]