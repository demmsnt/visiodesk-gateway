FROM python:3.7
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8 PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN rm requirements.txt

COPY ./data_collector.sh /data_collector.sh
#COPY ./docker/app.docker/linter.sh /linter.sh
RUN     chmod a+x /data_collector.sh
#        chmod a+x /linter.sh; 
