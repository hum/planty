# Planty
A personal bot for my server. This repo is intended only for educational purposes.

## TODO:
  - [ ] Db migration script
  - [ ] String sanitization for Db queries
  - [ ] Proper thread-safe requests
  - [ ] Rate limiting
  - [ ] Caching 
  - [ ] Tests

### Cogs
The available cogs are only ad-hoc solutions.
```bash
  /cogs
      hn.py     # Fetches Hackernews stories
      memes.py  # Fetches images from DB
      xkcd.py   # Fetches images from the XKCD API
```

### Setup configuration
The setup only requires to specify the PostgreSQL URI and the Discord token in the `planty/config.py` file.

```py
postgresql  = "postgresql://username:password@host:port/db_name"
TOKEN       = "" # discord bot token
```

### Requirements
  - Python      3.x
  - discord.py  1.5.x
  - urllib3     1.25.x
