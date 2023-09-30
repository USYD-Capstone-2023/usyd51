import requests

def main():

    res = requests.post("http://127.0.0.1:5000/signup", json={"username" : "sam", "password" : "passwd", "email" : "sam@same"})
    if res.status_code != 200:
        print(f"{res.content} {res.status_code}")

    res = requests.post("http://127.0.0.1:5000/login", json={"username" : "sam", "password" : "passwd"})
    if res.status_code != 200:
        print(f"{res.content} {res.status_code}")

    auth = res.content.decode("utf-8")
    print("Auth token is: %s\n" % auth)

    res = requests.post("http://127.0.0.1:5001/scan/-1", headers={"Auth-Token" : auth})
    if res.status_code != 200:
        print(f"{res.content} {res.status_code}")

    res = requests.get("http://127.0.0.1:5000/networks", headers={"Auth-Token" : auth})
    if res.status_code != 200:
        print(f"{res.content} {res.status_code}")

    print(res.content)


if __name__ == "__main__":
    main()