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

## Starting Planty
```bash
> cd planty
> docker build -t planty-bot .
> docker run -d planty-bot
```

If you want to set up [Sprout](https://github.com/hum/sprout) instance along with Planty then you need to also set `planty/sprout/configs/image.agent` and `planty/sprout/configs/db_config.json`

#### Start Planty with Sprout
```bash
# assumes a built binary (name: sprout) for Sprout in 'planty/sprout/build'
> cd planty
> docker-compose up --build -d 
```

#### Building Sprout from source
```bash
# alternatively clone from 'github.com/hum/sprout' codebase
> cd planty/sprout/src/sprout
> env GOOS=linux CGO_ENABLED=0 GOARCH=arm GOARM=5 \
    go build -v -o ../../build/sprout cmd/sprout/main.go
    #[GOOS, GOARCH, GOARM] -- platform flags
```

### Running Db
```🌱 TODO.```

### Requirements
  - Python      3.x
  - discord.py  1.5.x
  - urllib3     1.25.x
