# SoInsights API

## Heroku Deploy 
`cd backend`

### Install the Heroku CLI
https://devcenter.heroku.com/articles/heroku-cli


### Create a new app on Heroku
```bash
heroku create --buildpack https://github.com/moneymeets/python-poetry-buildpack.git so-insights-api
```

### Set the environment variables on Heroku
```bash
heroku config:set MONGODB_URI=mongodb://your-uri
heroku config:set MONGODB_DATABASE=the_name_of_the_db
```

### Deploy the app
```bash
git push heroku main
```

### Scale the app
```bash
heroku ps:scale web=1
```

### Open the app
```bash
heroku open
```