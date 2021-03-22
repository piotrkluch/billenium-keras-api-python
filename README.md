# billenium-keras-api-python

## 1. Prerequisites
- Python 3.8.8
- Aiohttp 3.7
- Tensorflow 2.0

&nbsp;\
&nbsp;

## 2. Setup
```
source ./setup-local-run.sh
```

...develop the code, programming part happens here...

If you want to leave the project and work from the same terminal, optionally you can:
```
deactivate
```

&nbsp;\
&nbsp;

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

&nbsp;\
&nbsp;

## 4. Run
Run with sh script:
```
./start-local-run.sh
```

&nbsp;\
&nbsp;

## 5. Deploy
### 5.1. Build docker image locally
```
make docker
```

Deploy to dev with
```
git push origin dev
```
