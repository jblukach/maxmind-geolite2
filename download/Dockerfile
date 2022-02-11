FROM public.ecr.aws/lambda/python:latest
RUN yum update -y
RUN pip install requests
COPY app.py ./
CMD ["app.lambdaHandler"]
