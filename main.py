#!/usr/bin/env python

import argparse
import sys
import requests
import os
import json


def run_query(query_name, header_auth, q_vars):
    with open('queries/' + query_name, 'r') as file:
        query = file.read().replace('\n', '')

    request = requests.post('https://api.github.com/graphql', json={'query': query, 'variables': q_vars }, headers=header_auth)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))


def get_repos(org, header_auth):
    """
    :param org: GitHub organisation name
    :param header_auth: {"Authorization": "Bearer " + github_token} #GitHub Personal Access Token
    :return: list of repositories available for this organisation

    GitHub has rate limits up to 100 nodes for each requests
    https://docs.github.com/en/free-pro-team@latest/graphql/overview/resource-limitations#node-limit
    If number of repos over 100 we must use pagination https://graphql.org/learn/pagination/
    """
    q_vars = {"q": org}
    result = run_query('get_first_repos.graphql', header_auth, q_vars)
    repos = []
    for repo in result["data"]["organization"]["repositories"]["edges"]:
        repos.append(repo["node"]["name"])
    while bool(result["data"]["organization"]["repositories"]["pageInfo"]["hasNextPage"]):
        cursor = result["data"]["organization"]["repositories"]["pageInfo"]["endCursor"]
        q_vars = {"q": org, "cursor": cursor}
        result = run_query('get_next_repos.graphql', header_auth, q_vars)
        for repo in result["data"]["organization"]["repositories"]["edges"]:
            repos.append(repo["node"]["name"])
    return repos


def get_branches(org, header_auth, repo):
    branches = ["branch1", "branch2"]
    return branches


def get_file_list(org, header_auth, repo, branch, search_dir):
    file_list = ["./ololo/zz.md", "./ololo/zz2.md"]
    return file_list


def parse_file(org, header_auth, repo, branch, filename, search_pattern):
    """
    query {
      repository(owner: "eastata", name: "zos-cli") {
        content:object(expression: "master:README.md") {
          ... on Blob {
            text
            isBinary
          }
        }
      }
    }
    """

    # Get test blob for file
    # execute search
    # Return:
    # * True if found
    # * False if not fund
    pass


def main():
    parser = argparse.ArgumentParser(description='Github search by all branches')
    parser.add_argument('--dir',
                        dest='dir',
                        default=".github/workflows/",
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
