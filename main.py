#!/usr/bin/env python

import argparse
import sys
import requests
import os
import re


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
    result = run_query('get_repos_first.graphql', header_auth, q_vars)
    repos = []
    for repo in result["data"]["organization"]["repositories"]["edges"]:
        repos.append(repo["node"]["name"])
    while bool(result["data"]["organization"]["repositories"]["pageInfo"]["hasNextPage"]):
        cursor = result["data"]["organization"]["repositories"]["pageInfo"]["endCursor"]
        q_vars = {"q": org, "cursor": cursor}
        result = run_query('get_repos_next.graphql', header_auth, q_vars)
        for repo in result["data"]["organization"]["repositories"]["edges"]:
            repos.append(repo["node"]["name"])
    return repos


def get_branches(org, header_auth, repo):
    q_vars = {"owner": org, "repo": repo}
    result = run_query('get_branches_first.graphql', header_auth, q_vars)
    branches = []
    for branch in result["data"]["repository"]["refs"]["edges"]:
        branches.append(branch["node"]["name"])
    while bool(result["data"]["repository"]["refs"]["pageInfo"]["hasNextPage"]):
        cursor = result["data"]["repository"]["refs"]["pageInfo"]["endCursor"]
        q_vars = {"owner": org, "repo": repo, "cursor": cursor}
        result = run_query('get_branches_next.graphql', header_auth, q_vars)
        for branch in result["data"]["repository"]["refs"]["edges"]:
            branches.append(branch["node"]["name"])
    return branches


def get_files(org, header_auth, repo, branch, search_dir):
    q_vars = {"owner": org, "repo": repo, "expression": branch + ":" + search_dir}
    result = run_query('get_files_first.graphql', header_auth, q_vars)
    files = []
    if result["data"]["repository"]["filename"]:
        for file in result["data"]["repository"]["filename"]["entries"]:
            if not bool(file["object"]["isBinary"]):
                files.append({"path": file["path"],
                              "text": file["object"]["text"]
                              })
    return files


def parse_files(files, pattern):
    matches = []
    for file in files:
        match = re.search(pattern, file["text"])
        if match:
            matches.append(file["path"])
    return matches


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
                        default="set-env|add-path",
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
    for repo in repos:
        branches = get_branches(args.org, header_auth, repo)
        for branch in branches:
            files = get_files(args.org, header_auth, repo, branch, args.dir)
            if files:
                matches = parse_files(files, args.pattern)
                print(f'git@github.com:{args.org}/{repo}.git -b {branch} \nFiles: {matches}')


if __name__ == '__main__':
    main()
