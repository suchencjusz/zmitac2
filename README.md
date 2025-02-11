# ZMiTAC 2

# project is being rewritten (branch: turbo)
https://github.com/suchencjusz/zmitac2/tree/turbo

ZMiTAC 2 is a simple application written in one (two) evenings, used to track pool games in DS. BABILON!!!

![ZMiTAC 2](https://raw.githubusercontent.com/suchencjusz/zmitac2/refs/heads/main/zmitac2.gif)
![kasia](https://raw.githubusercontent.com/suchencjusz/zmitac2/refs/heads/main/kasia-bilardzistka.gif)

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



