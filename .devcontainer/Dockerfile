FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

# Fix broken apt updates caused by an expired Yarn repo key
RUN rm -f /etc/apt/sources.list.d/yarn.list || true \
 && rm -f /etc/apt/trusted.gpg.d/yarn.gpg || true \
 && rm -f /usr/share/keyrings/yarn.gpg || true \
 && apt-get clean