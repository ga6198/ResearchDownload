import requests
import json
import pandas as pd
from string import Template
import wget
import urllib.request

query = """
{
  search(query: "mirror:false language:PHP stars:10 ", type: REPOSITORY, first: 100) {
    repositoryCount
    edges {
      node {
        ... on Repository {
          name
          description
          languages(first: 10) {
            edges {
              node {
                name
              }
            }
          }
          labels(first: 10) {
            edges {
              node {
                name
              }
            }
          }
          stargazers {
            totalCount
          }
          forks {
            totalCount
          }
          defaultBranchRef {
            target {
              ... on Commit {
                zipballUrl
              }
            }
          }
          updatedAt
          createdAt
          diskUsage
          primaryLanguage {
            name
          }
          id
          databaseId
          licenseInfo {
            name
          }
          url
          sshUrl
        }
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
  rateLimit {
    limit
    cost
    remaining
    resetAt
  }
}
"""

additional_query = Template("""
{
  search(query: "mirror:false language:PHP stars:10 ", type: REPOSITORY, first: 100, after: "$friendCursor") {
    repositoryCount
    edges {
      node {
        ... on Repository {
          name
          description
          languages(first: 10) {
            edges {
              node {
                name
              }
            }
          }
          labels(first: 10) {
            edges {
              node {
                name
              }
            }
          }
          stargazers {
            totalCount
          }
          forks {
            totalCount
          }
          defaultBranchRef {
            target {
              ... on Commit {
                zipballUrl
              }
            }
          }
          updatedAt
          createdAt
          diskUsage
          primaryLanguage {
            name
          }
          id
          databaseId
          licenseInfo {
            name
          }
          url
          sshUrl
        }
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
  rateLimit {
    limit
    cost
    remaining
    resetAt
  }
}

"""
)

def download_file(url):
    local_filename = url #url.split('/')[-1]
    # NOTE the stream=True parameter below
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                #if chunk: 
                f.write(chunk)
    return local_filename

def run_query(query):
    #authentication headers
    headers = {"Authorization": "Bearer a7555a39b691a217f6f060144755637a8378e2b3"}

    url = 'https://api.github.com/graphql'
    request = requests.post(url, json={'query': query}, headers=headers)

    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))

def download_projects(result):
    repos = result['data']['search']['edges']

    #download projects
    for entry in repos:
        projectUrl = entry['node']['url']
        downloadUrl = entry['node']['defaultBranchRef']['target']['zipballUrl']
        print(projectUrl)
        print(downloadUrl)
        wget.download(downloadUrl)

#initialize variables
result = None
hasNextPage = False
endCursor = None

continueFromLast = input("Continue using the last cursor from the previous run? (y/n)")

if continueFromLast == 'n':
    result = run_query(query)

    download_projects(result)

    hasNextPage = result['data']['search']['pageInfo']['hasNextPage']

elif continueFromLast == 'y':
    hasNextPage = True

if hasNextPage: #while hasNextPage:
    if continueFromLast == 'y':
        #open previous cursor from file
        file1 = open('finalCursor.txt', 'r')
        endCursor = file1.read()
        file1.close()

        #reset continuefromLast, so old key is not continuously used
        continueFromLast = None
    else:
        endCursor = result['data']['search']['pageInfo']['endCursor']

    new_query = additional_query.substitute({'friendCursor': endCursor}) #additional_query.format(friendCursor=endCursor)

    #print(new_query)

    result = run_query(new_query)

    #print(result)

    download_projects(result)

    hasNextPage = result['data']['search']['pageInfo']['hasNextPage']

    #end if there is no more data left
    remaining_rate_limit = result["data"]["rateLimit"]["remaining"] # Drill down the dictionary
    print("Remaining rate limit - {}".format(remaining_rate_limit))
    if remaining_rate_limit == 0:
        #write the remaining cursor
        file1 = open('finalCursor.txt', 'w')
        file1.write(endCursor)
        file1.close()
        break


#df_data = result['data']['search']['edges']
#df = pd.DataFrame(df_data)
#print(df)
