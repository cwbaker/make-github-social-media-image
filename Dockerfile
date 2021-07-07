FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN apt install libcairo2-dev pkg-config
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT [ "python", "./make-github-social-media-image.py" ]
