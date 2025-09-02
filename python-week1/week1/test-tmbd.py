import requests

url = "https://api.themoviedb.org/3/configuration"

headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIwNDhiNTQyMDUyYTg5ZjMxNWZhN2M2Yjc0YmQyNTNmOSIsIm5iZiI6MTc1NDgzMzA1OC45MTIsInN1YiI6IjY4OThhMGEyYWZjNjhhZTM1NDI2N2I1YiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.2SSJq7sLAlKopiSOFOonPLyZpZfT6dO8h6EItSWvGCg"
}

response = requests.get(url, headers=headers)

print(response.text)