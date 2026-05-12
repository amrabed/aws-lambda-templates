FROM mcr.microsoft.com/devcontainers/python:3

# Install and activate mise
RUN curl https://mise.run | sh && \
    echo 'eval "$(~/.local/bin/mise activate bash)"' >> ~/.bashrc

