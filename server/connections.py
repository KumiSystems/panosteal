import cgi

class IllegalMethodException(BaseException):
 pass

class InvalidArgumentException(BaseException):
 pass

class Request:
 def __init__(self, env = None):
  if env:
   self.fromEnv(env)

 def fromEnv(self, env):
  if env["REQUEST_METHOD"] == "POST":
   self.args = cgi.parse_qs(env['wsgi.input'].readline().decode(), True)
  elif env["REQUEST_METHOD"] == "GET":
   self.args = cgi.parse_qs(env['QUERY_STRING'], True)
  else:
   raise IllegalMethodException()

  self.path = env["PATH_INFO"].split("/")

  while "" in self.path:
      self.path.remove("")

  try:
    self.endpoint = self.path[0]
  except:
    self.endpoint = "index.html"

class Response:
 def __init__(self, status, ctype, content):
  self.status = status
  self.headers = [("Content-Type", ctype)]
  self.content = content

 def addHeader(self, name, value):
   self.headers.append((name, value))

