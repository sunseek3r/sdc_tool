FROM python:3.9

RUN apt-get update

RUN apt-get install -y \
    python3-pyqt5
    pyqt-dev-tools
    qttools5-dev-tools
    x11docker

WORKDIR /app

ADD . /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["x11docker", '--desktop', 'python', 'main.py']