import json

def distribute():
    '''
    Splits the id_to_url file into 4 files for processing
    '''
    id_to_url = None
    with open("../../databses/id_to_url.json", "r") as f:
        id_to_url = json.load(f)

    if not id_to_url:
        return
    
    urls = {}
    for i in range(len(id_to_url)):
        urls[str(i)] = id_to_url[str(i)]
        if i % 13848 == 0 and i != 0:
            json_file = f"../../databses/urlChunks/url_part_{i // 13848}.json"
            with open(json_file, "w") as out:
                json.dump(urls, out, indent=4)
            urls.clear()

        if i == 55392:
            json_file = f"../../databses/urlChunks/url_part_{(i// 13848) + 1}.json"
            with open(json_file, "w") as out:
                json.dump(urls, out, indent=4)
            urls.clear()

    return "Done chunking"

if __name__ == "__main__":
    print(distribute())
            