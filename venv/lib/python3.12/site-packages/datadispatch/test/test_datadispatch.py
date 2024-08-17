def test_example():
    from datadispatch import datadispatch

    @datadispatch(lambda args, _: args[0].get('type'))
    def handle(message):
      return ':('


    @handle.register('ping')
    def _(message):
      return 'you sent ping'


    @handle.register('pong')
    def _(message):
      return 'you sent pong'

    assert handle({'type': 'hello', 'payload': 'hello'}) == ':('
    assert handle({}) == ':('

    assert handle({'type': 'ping', 'payload': 'hello'}) == 'you sent ping'
    assert handle({'type': 'pong', 'payload': 'hello'}) == 'you sent pong'
