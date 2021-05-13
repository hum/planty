# Planty
<p align="center"><img src="static/planty.png" width="200" height="200" /></p>

------------------------------------------------------------------------------------------

A personal bot for my server. This repo is intended only for educational purposes.
## TODO:
  - [x] Set up proper permission system for cogs
  - [ ] Database migration script
  - [ ] String sanitization for database queries
  - [ ] Rate limiting

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
  - play [song/url]   # play a song in a specific voice channel
  - pause/resume    # pause or resume currently playing song
  - join/leave      # join or leave a voice channel
```

### Setup configuration
The setup only requires to specify the Discord token in the `config.py` file. Along with all values specified in the `.env` file. Or as an ENVIRONMENT variables if you don't plan to run it in a docker instance.

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
```

#### Run
```bash
> cd planty
> docker-compose up --build -d 
```

### Building Sprout-img from source
```bash
# alternatively clone from 'github.com/hum/sprout-img' codebase
> cd planty/sprout-img/sprout-img
> env GOOS=linux CGO_ENABLED=0 GOARCH=arm GOARM=5 \
    go build -v -o ../../build/sprout-img cmd/sprout-img/main.go
    #[GOOS, GOARCH, GOARM] -- platform flags
```

### Running Db
```🌱 TODO: Include migration script```

Planty works without a database, for now. The only use for a DB is to save images from the `sprout-img` instance and to store Twitch streamers to monitor. If you don't have a use for that, there's no need to set up a database.
