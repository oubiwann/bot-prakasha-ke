def send_commit(branch, rev_id):
    config = branch.get_config()
    host = config.get_user_option('message_host').encode('ascii')
    port = int(config.get_user_option('message_port'))
    password = config.get_user_option('message_password').encode('utf-8')
    channel = config.get_user_option('message_channel').encode('utf-8')
    branch_prefix = config.get_user_option('message_branch_prefix')

    nickname = branch.get_config().get_nickname()
    if branch_prefix:
        branch_prefix = branch_prefix.encode('utf-8')
        nickname = "%s/%s" % (branch_prefix, nickname)
    revision = branch.repository.get_revision(rev_id)
    message = ("%s r%d committed by %s\r\n%s"
               % (nickname, branch.revno(), branch.get_config().user_email(),
                  revision.message))
    import socket
    s = socket.socket()
    try:
        s.connect((host, port))
    except:
        print "Couldn't connect to publish-bot at %s:%s." % (host, port)
        return
        
    packit = ''
    for line in message.splitlines():
        packit += '%s:#%s:%s\r\n' % (password, channel, line)
    s.sendall(packit)
    s.close()
        
