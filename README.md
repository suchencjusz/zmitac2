# ZMiTAC 2

### todo:
- judges
- players mgmt
- rules
- player streak
- player matches today (count)
- better ranking (elo maybe?)
- additional info about match

### db:
- matches
  - winner(s)
  - losser(s)
  - billard gamemode

- player
  - points
  - judge
  - admin
  - password
  - description
  - achivements

### in future:
- api?
- notifactions (about new matches)
- bot for fandom dziekana (at least info about matches)

![1](https://raw.githubusercontent.com/suchencjusz/zmitac2/refs/heads/turbo/1.png)
![2](https://raw.githubusercontent.com/suchencjusz/zmitac2/refs/heads/turbo/2.png)

# Ussage

### docker compose

```
services:
  web:
    image: suchencjusz/zmitac2:main
    ports:
      - "5000:5000"
    environment:
      - MONGO_URI=mongodb+srv://
      - ADMIN_PASSWORD=dupa1234
    #volumes:
    # - ./custom.css:/app/app/static/styles.css
    restart: unless-stopped

  cloudflared:
    image: cloudflare/cloudflared
    command: tunnel --token ${TOKEN}
    restart: unless-stopped
```

### development

```
git clone https://github.com/suchencjusz/zmitac2
cd zmitac2
python3 -m venv venv

# activate venv

pip install -r requirements.txt
```

Linux
```source ./venv/Scripts/activate```

Windows
```.\venv\Scripts\activate```

# .env

```
DEBUG=True
PYTHONPATH=app
SECRET_KEY=
ADMIN_PASSWORD=
```
