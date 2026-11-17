FROM node:22-slim
WORKDIR /bot
COPY main.py .
COPY vendor/ vendor/
CMD ["python3", "-P", "-s", "/bot/main.py"]
