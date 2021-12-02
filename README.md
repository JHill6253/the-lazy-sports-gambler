# the-lazy-sports-gambler

private repo to store the lazy sports gamblers source code 


## Draft of prototype architecture 

![Architecture Map](./Docs/Images/TheLazyGambler.jpg)
## Dockerfiles 
### NBA_ML_BETS_API commands:
* Build image
```yaml
docker build -t nba_ml_bets_api:latest .
```
* run container
```yaml
docker run -d -p 5000:5000 nba_ml_bets_api
```
### Machine Learning commands:
* Build image
```yaml
docker build -t machine_learning:latest .
```
* run container
```yaml
docker run -d -p 5000:5000 machine_learning
```
### Text Service commands:
* Build image
```yaml
docker build -t text_service:latest .
```
* run container
```yaml
docker run -d -p 5000:5000 text_service
```
