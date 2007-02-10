HOST = 'commitbot.example.com'
PORT = 1234
PASSWORD = 'password'
CHANNEL = '#channel'

def send_commit(branch, rev_id):
    revision = branch.repository.get_revision(rev_id)
    message = "%s [%s] - %s" % (revision.committer,
                                branch.get_config().get_nickname(),
                                revision.message)
    import socket
    s = socket.socket()
    s.connect((HOST, PORT))
    for line in message.splitlines():
        packit = '%s:%s:%s\r\n' % (PASSWORD, CHANNEL, line)
        s.sendall(packit)
    s.close()
