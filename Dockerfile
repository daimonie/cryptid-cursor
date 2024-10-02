# Use Python 3.12.3 as the base image
FROM python:3.12.3

# Update the debian packages
RUN apt-get update

# Install pre-commit
RUN apt install pre-commit -y

# Install poetry
RUN pip install poetry

# Verify poetry installation
RUN poetry --version

# Copy container directory into docker image
COPY container/ /opt/container

# Set working directory
WORKDIR /opt/container

# Create a group and user for restricted access
RUN groupadd -r python-role && useradd -r -g python-role pythonuser

# Switch to root user for setting permissions
USER root
RUN echo "root:cthulu" | chpasswd

# Ensure pythonuser can run python files
RUN chmod +x /opt/container/*.py

# Grant read/write access to home directory for poetry
RUN chmod a+rw /home

# Set permissions for /opt/container and /opt/container/output
RUN chown -R root:python-role /opt/container && \
    chmod -R 755 /opt/container && \ 
    mkdir -p /opt/container/output && \
    chown -R pythonuser:python-role /opt/container/output && \
    chmod -R 775 /opt/container/output

# Install poetry dependencies for root
RUN poetry install 