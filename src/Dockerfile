FROM python:3.10.12

WORKDIR /readings/src

COPY . .

RUN pip install fastapi
RUN pip install "uvicorn[standard]"
RUN pip install requests
RUN pip install pydantic
RUN pip install SQLAlchemy
RUN pip install scikit-surprise
RUN pip install psycopg2

EXPOSE 8000

CMD ["sh", "-c", "uvicorn main:app --reload"]