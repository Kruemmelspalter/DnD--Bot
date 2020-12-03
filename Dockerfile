FROM python

WORKDIR /root

RUN ["python", "-m", "pip", "install", "--upgrade", "pip"]

COPY requirements.txt .

RUN ["pip", "install", "-r", "requirements.txt"]

COPY etc_dndtools-discord/ /etc/dndtools-discord

COPY src/ .

CMD ["python3", "main.py"]
