FROM fedora:35

# RUN dnf update -y

RUN dnf install -y bash coreutils iproute iputils procps-ng

RUN dnf install -y "@Development Tools"

RUN dnf install -y python-devel vim-enhanced openssl



WORKDIR /pcp-app

RUN useradd --create-home pcp



RUN mkdir /pcp-app/ -p

RUN chown pcp.pcp /pcp-app



RUN mkdir /run/pcp-app -p

RUN chown pcp.pcp /run/pcp-app



RUN mkdir /srv/pcp/logs/ -p

RUN chown pcp.pcp /srv/pcp/logs



COPY requirements.txt /tmp



RUN chown pcp.pcp /tmp/requirements.txt

RUN mkdir /pcp-env

RUN chown pcp.pcp /pcp-env



RUN dnf    install    -y python3.9

RUN dnf    install    -y wget

RUN wget https://bootstrap.pypa.io/get-pip.py

RUN python3.9 get-pip.py



USER pcp



RUN python3.9 -m venv /pcp-env

# RUN /pcp-env/bin/pip install --upgrade pip==22.0.4 setuptools



# RUN /pcp-env/bin/pip install pip-tools



RUN /pcp-env/bin/pip install -r /tmp/requirements.txt --disable-pip-version-check --trusted-host pypi.python.org -r /tmp/requirements.txt --no-cache-dir



COPY --chown=pcp ./containerize/pcp-container-exec-development.sh /usr/local/bin