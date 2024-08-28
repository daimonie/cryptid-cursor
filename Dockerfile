from python:3.12.3

# update the debian packages
RUN apt-get update
RUN apt install pre-commit -y

# install poetry
RUN pip install poetry
RUN poetry --version


# copy container directory into docker image, move to it
COPY container/ /opt/container
WORKDIR /opt/container

# Create a group and user for restricted access
RUN groupadd -r python-role && useradd -r -g python-role pythonuser

# Create a dev user with sudo privileges
RUN useradd -m -s /bin/bash devuser && \
    usermod -aG sudo devuser && \
    echo "devuser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Additional read/write for container & home
RUN chmod a+rw /opt/container/
RUN chmod a+rw /home

# Set password for devuser (change 'password' to your desired password)
RUN echo 'devuser:cthulu' | chpasswd

# Switch to pythonuser for default operation
USER pythonuser

# install poetry from pypoetry.toml
RUN poetry install
