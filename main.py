#!/usr/bin/env python

import argparse
import sys
import requests
import os
import json


def run_query(query, header_auth):
    request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=header_auth)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))


def get_repos(org, header_auth):
    with open('get_repos.graphql', 'r') as file:
        data = file.read().replace('\n', '')
        #print(data)

    q_vars = {'org': 'clearmatics', 'cursor': 'ASDASDASD='}
    query = data + json.dumps(q_vars)

    print(query)

    result = run_query(query, header_auth)
    print(json.dumps(result))

    
    sys.exit(0)

    repos = {}
    for repo in result["data"]["search"]["edges"]:
        branches = []
        for branch in repo["node"]["refs"]["edges"]:
            branches.append(branch["node"]["name"])
        repos |= {repo["node"]["nameWithOwner"]: branches}
    return repos


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

    header_auth = {"Authorization": "Bearer " + github_token}
    repos = get_repos(args.org, header_auth)
    print(json.dumps(repos))


if __name__ == '__main__':
    main()
