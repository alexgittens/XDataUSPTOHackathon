# run this to setup jupyter on an AWS instance launched from an Anaconda community (Ubuntu) AWS image
# the password is tools
#!/bin/bash

CERTIFICATE_DIR="/home/ubuntu/certificate"
JUPYTER_CONFIG_DIR="/home/ubuntu/.jupyter"

if [ ! -d "$CERTIFICATE_DIR" ]; then
    mkdir $CERTIFICATE_DIR
    openssl req -x509 -nodes -days 365 -newkey rsa:1024 -keyout "$CERTIFICATE_DIR/mykey.key" -out "$CERTIFICATE_DIR/mycert.pem" -batch
    chown -R ubuntu $CERTIFICATE_DIR
fi

if [ ! -f "$JUPYTER_CONFIG_DIR/jupyter_notebook_config.py" ]; then
    # generate default config file
    #jupyter notebook --generate-config
    mkdir $JUPYTER_CONFIG_DIR

    # append notebook server settings
    cat <<EOF >> "$JUPYTER_CONFIG_DIR/jupyter_notebook_config.py"
# Set options for certfile, ip, password, and toggle off browser auto-opening
c.NotebookApp.certfile = u'$CERTIFICATE_DIR/mycert.pem'
c.NotebookApp.keyfile = u'$CERTIFICATE_DIR/mykey.key'
# Set ip to '*' to bind on all interfaces (ips) for the public server
c.NotebookApp.ip = '*'
c.NotebookApp.password = u'sha1:b2f61058d4d4:209e4db4d773b14a00924d0f893391daf7baa872'
c.NotebookApp.open_browser = False

# It is a good idea to set a known, fixed port for server access
c.NotebookApp.port = 8888
EOF
    chown -R ubuntu $JUPYTER_CONFIG_DIR
fi

