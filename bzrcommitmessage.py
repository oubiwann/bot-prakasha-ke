HOST = 'commitbot.example.com'
PORT = 1234
PASSWORD = 'password'
CHANNEL = '#channel'

def send_commit(branch, rev_id):
    message = branch.repository.get_revision(rev_id).message
    import socket
    s = socket.socket()
    s.connect((HOST, PORT))
    packit = '%s:%s:%s\r\n' % (PASSWORD, CHANNEL, message)
    s.send(packit)
    s.close()
