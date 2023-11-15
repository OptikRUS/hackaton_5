# установка python 3.11 с официального докерхаба
FROM python:3.11.5

# хост базы данных для докера
ENV SITE_HOST=0.0.0.0

# установка рабочей директории
WORKDIR /

# установка зависимостей
COPY pyproject.toml .
RUN pip install poetry  \
    && poetry config virtualenvs.create false \
    && poetry install --no-ansi --no-cache

# копирование проекта
COPY . .

RUN pip install opencv-python==4.8.1.78
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
