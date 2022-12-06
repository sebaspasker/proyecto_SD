import json

data = {
    "cities": [
        "Rome",
        "Amsterdam",
        "Atenas",
        "Madrid",
        "Oslo",
        "Madrid",
        "Alicante",
        "Barcelona",
        "Bilbao",
        "Paris",
        "Berlin",
        "Budapest",
        "London",
        "Helsinki",
        "Abu Dabi",
    ]
}


with open("./json/cities.json", "w") as outfile:
    str_ = json.dumps(data)
    outfile.write(str_)
