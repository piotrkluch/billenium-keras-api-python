# billenium-keras-api-python

## 1. Prerequisites
```
    - Python 3.8
    - Aiohttp 3.7
    - Tensorflow 2.0
```

## 2. Setup
```
    source ./setup_local_run.sh
```

...develop the code, programming part happens here...

If you want to leave the project and work from the same terminal, optionally you can:
```
    deactivate
```

## 3. Test
### 3.1. Test from CLI
```
    make tests
```

### 3.2. Test from IDE
Open VS Code then, do:
```
    [CMD + SHIFT + P]
    >discover unit tests
    [Enter]
```

## 4. Run
Run with sh script:
```
    ./start_local_run.sh
```

## 5. Deploy
### 5.1. Build docker image locally
```
    make docker
```

Deploy to dev with
```
    git push origin dev
```
