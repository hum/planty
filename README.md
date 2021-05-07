# Planty
<p align="center"><img src="static/planty.png" width="200" height="200" /></p>

------------------------------------------------------------------------------------------

A personal bot for my server. This repo is intended only for educational purposes.
## TODO:
  - [ ] Set up proper permission system for cogs
  - [ ] Database migration script
  - [ ] String sanitization for database queries
  - [ ] Proper thread-safe requests
  - [ ] Rate limiting
  - [ ] Caching 

### Cogs
The available cogs are only ad-hoc solutions.
```bash
  /cogs
      hn.py      # Fetches Hackernews stories
      memes.py   # Fetches images from DB
      xkcd.py    # Fetches images from the XKCD API
      twitch.py  # Notifies users whenever a certain streamer goes live
      code.py    # Returns code for the specified command
      message.py # Prunes and snipes messages
```

### Commands
All available commands for Planty
```bash
> [prefix]            # 'planty ', 'Planty ', '.p ', '.P ', '🌱 '
  - hn                # sends (default=10) posts from Hackernews' API
  - meme              # sends an image randomly chosen from the DB
  > sub
    - list            # lists all available image sources          
    - add [name]      # adds an image source to the db
    - remove [name]   # removes an image source from the db
  > img
    - fetch           # harvests images from all of the available sources
    - prune           # deletes old images from the db (default=14 days)
  > twitch
    - add [name]      # adds the streamer to the list
    - remove [name]   # removes the streamer from the list
  - xkcd              # sends an xkdc comic
  - snipe             # shows the last deleted message
  - prune             # deletes (default=1) messages posted in the chat
  - source [command]  # returns the code and the link for the specific command 
```

### Setup configuration
The setup only requires to specify the Discord token in the `config.py` file. Along with `TWITCH_CLIENT_ID`, `TWITCH_AUTHORIZATON`, and `POSTGRE_URI` tokens in the `.env` file. Or as an ENVIRONMENT variable if you don't plan to run it in a docker instance.

```ini
# config.py
TOKEN       = "" # discord bot token

# .env file or export as ENV variable
TWITCH_CLIENT_ID=5593daz4asdqrewqgxzxcz         # Will be used by Sprout-img instead SoonTM
TWITCH_AUTHORIZATION=Bearer fga852s4a56ad4aa6   # Will be used by Sprout-img instead SoonTM
POSTGRE_URI=postgres://user:password@host:port/db_name?sslmode=disable
```

## Starting Planty
```bash
> cd planty
> docker build -t planty-bot .
> docker run -d planty-bot

# alternatively just
> pip install -r requirements.txt
> python3 run.py
```

#### Start Planty with Sprout-img
If you want to set up [Sprout-img](https://github.com/hum/sprout-img) instance along with Planty then you need to also   set some ENV values.

```ini
# .env

REDDIT_USERNAME=username
REDDIT_PASSWORD=password
REDDIT_CLIENT_SECRET=d-qwerty15AsesdsxaE5sa
REDDIT_CLIENT_ID=D45sx2-d4xayt
REDDIT_USER_AGENT=Darwin:github.com/hum/sprout-img:0.0.2 (by /u/username)

# already set
POSTGRE_URI=postgres://user:password@host:port/db_name?sslmode=disable
```

#### Run
```bash
# assumes a built binary (name: sprout-img) for Sprout in 'planty/sprout-img/build'
> cd planty
> docker-compose up --build -d 
```

### Building Sprout from source
```bash
# alternatively clone from 'github.com/hum/sprout-img' codebase
> cd planty/sprout-img/sprout-img
> env GOOS=linux CGO_ENABLED=0 GOARCH=arm GOARM=5 \
    go build -v -o ../../build/sprout-img cmd/sprout-img/main.go
    #[GOOS, GOARCH, GOARM] -- platform flags
```

### Running Db
```🌱 TODO.```
