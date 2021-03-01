# Planty
<p align="center"><img src="https://www.flaticon.com/svg/vstatic/svg/1752/1752933.svg?token=exp=1614607468~hmac=3f1f290c1c0ee3a75004b1901ec68b40" width="300" height="300" /></p>

A personal bot for my server. This repo is intended only for educational purposes.
## TODO:
  - [ ] Add more cogs
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

### Commands
All available commands for Planty
```bash
> [prefix]          # 'planty ', 'Planty ', '.p ', '.P ', '🌱 '
  - hn              # sends (default=10) posts from Hackernews' API
  - meme            # sends an image randomly chosen from the DB
  > sub
    - list          # lists all available image sources          
    - add [name]    # adds an image source to the db
    - remove [name] # removes an image source from the db
  > img
    - fetch         # harvests images from all of the available sources
    - prune         # deletes old images from the db (default=14 days)
  > twitch
    - add [name]    # adds the streamer to the list
    - remove [name] # removes the streamer from the list
  - xkcd            # sends an xkdc comic
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

If you want to set up [Sprout-img](https://github.com/hum/sprout-img) instance along with Planty then you need to also   set `planty/sprout-img/build/db_config.json` values.

#### Start Planty with Sprout-img
```bash
# assumes a built binary (name: sprout-img) for Sprout in 'planty/sprout-img/build'
> cd planty
> docker-compose up --build -d 
```

#### Building Sprout from source
```bash
# alternatively clone from 'github.com/hum/sprout' codebase
> cd planty/sprout-img/sprout-img
> env GOOS=linux CGO_ENABLED=0 GOARCH=arm GOARM=5 \
    go build -v -o ../../build/sprout-img cmd/sprout-img/main.go
    #[GOOS, GOARCH, GOARM] -- platform flags
```

### Running Db
```🌱 TODO.```

### Requirements
  - Python      3.x
  - discord.py  1.5.x
  - urllib3     1.25.x
