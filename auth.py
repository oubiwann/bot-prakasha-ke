from twisted.protocols import http
from twisted.web import resource, util, error
from twisted.cred import portal, checkers, credentials

from twisted.web.woven import simpleguard

class BasicAuthWrapper(resource.Resource):

    def __init__(self, portal, basicRealm="default"):
        resource.Resource.__init__(self)
        self.portal = portal
        self.basicRealm = basicRealm

    def getChild(self, path, request):
        def loginSuccess(result):
            interface, avatar, logout = result
            return avatar.getChildWithDefault(path, request)

        def loginFailure(error):
            return BasicAuthError(http.UNAUTHORIZED, "Unauthorized",
                "401 Authentication required", self.basicRealm)
        username = request.getUser()
        password = request.getPassword()
        d = self.portal.login(credentials.UsernamePassword(username, password),
            None, resource.IResource)
        d.addCallbacks(loginSuccess, loginFailure)
        return util.DeferredResource(d)

class BasicAuthError(error.ErrorPage):

    def __init__(self, status, brief, detail, basicRealm="default"):
        error.ErrorPage.__init__(self, status, brief, detail)
        self.basicRealm = basicRealm

    def render(self, request):
        request.setHeader('WWW-authenticate', 'Basic realm="%s"' %
            self.basicRealm)
        return error.ErrorPage.render(self, request)


def guardResourceWithBasicAuth(resource, realm, db):
    logPortal = portal.Portal(simpleguard.MarkingRealm(resource))
    checker = checkers.InMemoryUsernamePasswordDatabaseDontUse
    checker = checker(**db)
    logPortal.registerChecker(checker)
    return BasicAuthWrapper(logPortal, realm)
