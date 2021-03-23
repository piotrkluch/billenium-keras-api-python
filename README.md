# billenium-keras-api-python





| Table of Contents |
|---|
|1. Screenshot|
|2. Prerequisites|
|3. Setup|
|4. Test|
|5. Run|
|6. Deploy|
|7. Notes|


&nbsp;

---

&nbsp;\
&nbsp;

## 1. Screenshot

![screenshot](./docs/media/screenshot.png)

&nbsp;\
&nbsp;

## 2. Prerequisites
- Python 3.8.8
- Aiohttp 3.7
- Tensorflow 2.0

&nbsp;\
&nbsp;

## 3. Setup
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

## 4. Test
### 4.1. Test from CLI
```
make tests
```

### 4.2. Test from IDE
Open VS Code, then do:
```
[CMD + SHIFT + P]
>discover unit tests
[Enter]
```

&nbsp;\
&nbsp;

## 5. Run
### 5.1. Run from CLI
```
./start-local-run.sh
```

### 5.2. Run from IDE
Open VS Code, then do:
```
[FN + 5] / [F5]
```

&nbsp;\
&nbsp;

## 6. Deploy
### 6.1. Build docker image locally
```
make docker
```

Deploy to dev with
```
git push origin dev
```

&nbsp;\
&nbsp;

## 7. Notes
Swagger/OpenAPI spec is available after the server has started under URI: http://127.0.0.1:8080/docs