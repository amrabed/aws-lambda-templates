FROM mcr.microsoft.com/devcontainers/python:3.14

# Install mise
RUN curl https://mise.run | sh
ENV PATH="/root/.local/share/mise/bin:/root/.local/share/mise/shims:$PATH"

# Install AWS CDK CLI
RUN npm install -g aws-cdk
