# Build Custom Python Docker Image [https://docs.docker.com/language/python/build-images/](https://docs.docker.com/language/python/build-images/)
Als Basisimage wird hier *python:3.8-slim-buster* verwendet. Dieses enthält bereits das Python Modul *pip* welches zum installieren weiterer Pakete benötigt wird. Es braucht hier nur mehr das Image gebaut werden. Der Vollständigkeit halber sind im Absatz [Vorbereitung](#Vorbereitung) alle Schritte und durchgeführte Änderungen beschrieben.

## Build Image
```bash
docker build --tag irkfish:python38 .
```

## run example
```bash
docker-compose up -d
```

## Vorbereitung 
### Bestimmen der zu Installierenden Python Packages
Bevor das Dockerfile erstellt wird müssen zuerst die Python Pakete bestimmt werden welche im Image benötigt werden. Dies kann durch einen Testlauf im Basisimage erfolgen.

1. Run docker image with files
    ```bash
    docker run -it --rm --name rowa-python -v C:\Users\ak192053\Documents\tmp\vscode\rowa\03_FiwareConnector_MachiningCentre:/app python:3.8-slim-buster bash
    ```
2. Start Python script ()
    ```bash
    cd /app
    pip3 install watchdog requests
    pip3 freeze >> requirements.txt
    ```
3. Problem mit Observer
    
    Laufwerk I: Muss dem Container bereitgestellt werden! Dies erfolgt im docker-compose file.
    ```bash
    root@c58f9f391665:`python3 irkfish.py
    Traceback (most recent call last):
        File "irkfish.py", line 148, in <module>
            observer.start()
        File "/usr/local/lib/python3.8/site-packages/watchdog/observers/api.py", line 262, in start
            emitter.start()
        File "/usr/local/lib/python3.8/site-packages/watchdog/utils/__init__.py", line 93, in start
            self.on_thread_start()
        File "/usr/local/lib/python3.8/site-packages/watchdog/observers/inotify.py", line 118, in on_thread_start
            self._inotify = InotifyBuffer(path, self.watch.is_recursive)
        File "/usr/local/lib/python3.8/site-packages/watchdog/observers/inotify_buffer.py", line 35, in __init__
            self._inotify = Inotify(path, recursive)
        File "/usr/local/lib/python3.8/site-packages/watchdog/observers/inotify_c.py", line 169, in __init__
            self._add_watch(path, event_mask)
        File "/usr/local/lib/python3.8/site-packages/watchdog/observers/inotify_c.py", line 386, in _add_watch
            Inotify._raise_error()
        File "/usr/local/lib/python3.8/site-packages/watchdog/observers/inotify_c.py", line 406, in _raise_error
            raise OSError(err, os.strerror(err))
        FileNotFoundError: [Errno 2] No such file or directory
    ```

    Anpassungen docker-compose.yml
    ```
    volumes:
      - I:\Irkfish:/app/Irkfish
    ```
            
    Anpassungen irkfish.py:

    ```python
    #mount I:\Irkfish\ to /app/Irkfish in docker-compose.yml
    #local_path = r'I:\Irkfish\Irkfish'
    local_path = r'/app/Irkfish/Irkfish'
    #sim_path = r'I:\Irkfish\Original_SIM'
    sim_path = r'/app/Original_SIM'
    #filename = r"\Irkfish"
    filename = r"/app/Irkfish"
    host = "10.10.65.1"

    ocb_hostname = os.getenv("ORION_HOST", "orion") #set hostname in docker-compose file
    ocb_port = os.getenv("ORION_HOST", "1026") #set port in docker-compose file
    urlOrion = "http://{}:{}}".format(ocb_hostname,ocb_port)
    ```




    
