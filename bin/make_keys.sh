KEY_DIR=`python -c "from publishbot import config;print config.ssh.keydir"`
mkdir -p $KEY_DIR
ckeygen -t rsa -f $KEY_DIR/id_rsa