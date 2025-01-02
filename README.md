



## Setup Virtual Env

```
sudo pip3 install virtualenv
python3 -m venv .venv

source .venv/bin/activate
```

Then install dependencies

```
python3 -m pip install -r requirements.txt
```

## Install OpenSearch

```
brew install opensearch
```

Once completed, install the KNN plugin

```
opensearch-plugin install https://repo1.maven.org/maven2/org/opensearch/plugin/opensearch-knn/2.18.0.0/opensearch-knn-2.18.0.0.zip
```


## Run OpenSearch

```
/opt/homebrew/opt/opensearch/bin/opensearch
``` 