from http.server import BaseHTTPRequestHandler, HTTPServer
import random
import time


class DiceServer(BaseHTTPRequestHandler):
  def do_GET(self):
    """Expects a request like of the form '/d20/ActionName"""
    # TODO(gregable): Make this return something on parse error rather than
    # simply throwing an exception.
    parts = self.path.split("/")
    # ['d20', 'ActionName']

    # TODO(gregable): Unescape percent-escaped input, like `%2B` (+), space,
    # etc.

    self.send_response(200)
    self.send_header("Content-type", "text/html")
    # Facebook Messenger seems to ignore Cache-Control headers unfortunately:
    self.send_header("Cache-Control", "max-age=5")
    self.end_headers()
    self.wfile.write(bytes("<!doctype html>", "utf-8"))
    self.wfile.write(bytes("<html>", "utf-8"))
    self.wfile.write(bytes("<head>", "utf-8"))
    self.wfile.write(bytes("<title>", "utf-8"))
    self.wfile.write(bytes(parts[2], "utf-8"))

    self.RollDice(parts[1])

    self.wfile.write(bytes("</title>", "utf-8"))
    self.wfile.write(bytes("</head>", "utf-8"))
    self.wfile.write(bytes("<body>", "utf-8"))
    self.wfile.write(bytes("</body>", "utf-8"))
    self.wfile.write(bytes("</html>", "utf-8"))

  def RollDice(self, cmd):
    """Supports format like `XdY+Z`, example: `6d6+2`."""
    # TODO(gregable): This entire parsing routine is brittle. Improve.

    # XdY+Z:
    # - X is dice `mult`
    # - Y is dice `sides`
    # - Z is dice `mod`
    parts = cmd.split('+')
    if len(parts) == 1:
      mod = 0
    else:
      mod = int(parts[1])

    if mod == 0:
      parts = cmd.split('-')
      if len(parts) == 1:
        mod = 0
      else:
        mod = -1 * int(parts[1])

    # TODO(gregable): Support capitals 'D'.
    parts = parts[0].split('d')
    if parts[0] == '':
      mult = 1
    else:
      mult = int(parts[0])

    sides = int(parts[1])

    if mod > 0:
      self.wfile.write(bytes(" (%dD%d+%d) = " % (mult, sides, mod), "utf-8"))
    elif mod < 0:
      # We don't need the `-` because `mod` is negative.
      self.wfile.write(bytes(" (%dD%d%d) = " % (mult, sides, mod), "utf-8"))
    else:
      self.wfile.write(bytes(" (%dD%d) = " % (mult, sides), "utf-8"))

    result = mod
    # For each die, roll random, print it's value and add it to the result.
    for i in range(mult):
      roll = random.randint(1, sides)
      if i + 1 < mult:
        self.wfile.write(bytes("%d+" % roll, "utf-8"))
      else:
        self.wfile.write(bytes("%d" % roll, "utf-8"))
      result += roll

    # Print the mod, if one is present and the result.
    if mod > 0:
      self.wfile.write(bytes("+%d: %d" % (mod, result), "utf-8"))
    elif mod < 0:
      self.wfile.write(bytes("%d: %d" % (mod, result), "utf-8"))
    else:
      self.wfile.write(bytes(": %d" % result, "utf-8"))


if __name__ == "__main__":
  webServer = HTTPServer(("localhost", 8000), DiceServer)

  try:
    webServer.serve_forever()
  except KeyboardInterrupt:
    print("Caught KeyboardInterrupt, exiting...")
  finally:
    webServer.server_close()
    print("Server stopped.")
