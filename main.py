#!/usr/bin/env python

import argparse
import sys
import requests
import os
import json


def run_query(query, headers):
    request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))


def main():
    parser = argparse.ArgumentParser(description='Github search by all branches')
    parser.add_argument('--dir',
                        dest='dir',
                        default="./",
                        type=str,
                        help='Dir for search (default: %(default)s)'
                        )
    parser.add_argument('--org',
                        dest='org',
                        default="clearmatics",
                        type=str,
                        help='GitHub organisation (default: %(default)s)'
                        )
    parser.add_argument('--pattern',
                        dest='pattern',
                        default="set-env",
                        type=str,
                        help='Search pattern (default: %(default)s)'
                        )
    args = parser.parse_args()

    try:
        github_token = os.environ["GITHUB_PAT"]
    except KeyError:
        print("Error. GitHub PAT must be provided via environment variable")
        print("export GITHUB_PAT=")
        sys.exit(1)

    query = """
    {
      search(query: "org:""" + args.org + """", type: REPOSITORY, first: 3) {
        repositoryCount
        edges {
          node {
            ... on Repository {
              nameWithOwner,
              refs(first: 100, refPrefix: "refs/heads/") {
                edges{
                  node {
                    name
                  }
                }
              }
            }
          }
        }
      }
    }
    """

    result = run_query(query, {"Authorization": "Bearer " + github_token})
    print(json.dumps(result["data"]["search"], sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
