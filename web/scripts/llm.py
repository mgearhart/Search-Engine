import requests
import json

url_to_summary = {}
id_to_url = {}

def summarize(path: str):
    '''
    Uses the phi3 LLM to summarize the contents of the url. Installation of the model
    can be found in the readme
    '''
    with open(path, "r") as map:
        id_to_url = json.load(map)   

        for id, url in id_to_url.items():
            llm_url = "http://localhost:11434/api/generate"
            prompt = "Here is the content of a webpage in 6-10 words analyze the it and summarize the page.\
                            Make sure the summary is short and speedy, here is the url: " + str(url)
            llm_data = {
                "model": "phi3",
                "prompt": prompt,
                "stream": False
            }

            headers = {
                'Content-Type': 'application/json'
                }

            response = requests.post(llm_url, data=json.dumps(llm_data), headers=headers)

            if response.status_code == 200:
                summary = response.json()["response"]
            else:
                summary = "Unable to retrieve page details."

            url_to_summary[id] = summary
            print(f"{id:<6} {summary}")
                
                

if __name__ == "__main__":
    # put in the path of the json file ex) "../../databases/url_part_1.json"
    summarize("../../databases/id_to_url.json")

    # change the name of the file that it is saved to
    with open("../../databases/id_to_summary_part1.json", "w") as out:
        json.dump(url_to_summary, out, indent=4)