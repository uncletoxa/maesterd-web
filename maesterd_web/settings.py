from environs import env

env.read_env()

MAX_TITLE_LENGTH = env.int('MAX_TITLE_LENGTH', default=140)
STORIES_PER_PAGE = env.int('STORIES_PER_PAGE', default=20)
CHAPTERS_PER_PAGE = env.int('CHAPTERS_PER_PAGE', default=1000)  # I have no idea how to do a pagination with prompt
OPENAI_SOCKET_ADDR = env.str('OPENAI_SOCKET_ADDR', '/tmp/sockets/openai_service.sock')