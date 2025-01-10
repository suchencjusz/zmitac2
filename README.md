# ZMiTAC 2

### todo:
- fix: match between x vs x should not be possible
- docker (almost)
- finish it
- i need goofy css
- basic stats
- najbardziej zdeklasowani przeciwnicy

### in future:
- goofy bot for fandom dziekana

ZMiTAC 2 is a simple application written in one (two) evenings, used to track pool games in DS. BABILON!!!

![ZMiTAC 2](https://raw.githubusercontent.com/suchencjusz/zmitac2/refs/heads/main/image.png)

# Ussage

### docker compose

```
version: '3.8'

services:
  web:
    build: suchencjusz/zmitac2:main
    ports:
      - "5000:5000"wtf i want t
    environment:
      - MONGO_URI=mongodb+srv://
      - ADMIN_PASSWORD=dupa1234
    volumes:
      - .:/app
      # - ./custom.css:/app/app/static/styles.css
    restart: unless-stopped

  cloudflared:
    image: cloudflare/cloudflared
    command: tunnel --url http://web:5000
    environment:
      - TUNNEL_HOSTNAME=example.com
    restart: unless-stopped
```

### development

```
git clone https://github.com/suchencjusz/zmitac2
cd zmitac2
python3 -m venv venv
```

Linux
```source ./venv/Scripts/activate```

Windows
```.\venv\Scripts\activate```



