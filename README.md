# Movie Collector

A movie collector pipeline build to illustrate how OOP fits data pipeline.

## Setup

```
cd movie-collector
poetry shell
make check
```

## Usage
```{python}
from movie_collector import MovieCollector
collector = MovieCollector(api_key=<your-api-key>, download_new=True)
df = collector.run()
```