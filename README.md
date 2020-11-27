# Yet another one github search
Github search by all branches

## Usage
Generate new `Personal Access Token` for [GitHub](https://github.com/settings/tokens)

```bash
export GITHUB_PAT=%GITHUB PERSONAL ACCESS TOKEN%

docker run --rm --env GITHUB_PAT eastata/yet-another-one-github-search \
    --org "clearmatics"\
    --dir ".github/workflows" \
    --pattern "set-env"
```

## CLI options

```
optional arguments:
  -h, --help         show this help message and exit
  --dir DIR          Dir for search (default: ./)
  --org ORG          GitHub organisation (default: clearmatics)
  --pattern PATTERN  Search pattern (default: set-env)
```

## Build
```
docker build -t eastata/yet-another-one-github-search:latest .
```

## Links
* [GitHub's GraphQL Explorer ](https://developer.github.com/v4/explorer/)
