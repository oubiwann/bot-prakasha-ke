from carapace.sdk.exceptions import Error


class MissingSSHServerKeysError(Error):
    """
    SSH server keys not found. Generate them with ./bin/make-keys.sh.
    """


class IllegalAPICommand(Error):
    """
    """
