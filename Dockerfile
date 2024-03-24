FROM public.ecr.aws/lambda/python:3.10

WORKDIR /var/task

COPY ./Pipfile ./Pipfile.lock ./

RUN pip install pipenv && \
    pipenv install --system --deploy --ignore-pipfile


COPY ./main ./

CMD ["app.handler"]