import requests
import json
import os

url_to_summary = {}

def summarize():
     id_count = 0

     dev_path = os.path.abspath("../../DEV")

     for root, dirs, files in os.walk(dev_path): #loop through DEV directory and subdirectories
        dirs.sort()                 
        for file in sorted(files):  
            file_path = os.path.join(root, file) #Get absolute path to file so we can open it
                
            with open(file_path, "r") as f: #open file then grab data from json file
                data = json.load(f)
                
                url = data.get("url", "") # Our data from the json
                content = data.get("content", "")

                llm_url = "http://localhost:11434/api/generate"
                prompt = "Here is the content of a webpage in 6-10 words analyze the it and summarize the page.\
                          Make sure the summary is short and speedy, here is the url: " + str(content)
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

                url_to_summary[id_count] = summary
                print(f"{id_count:<6} {summary}")

                id_count += 1

                
                
                

if __name__ == "__main__":
    summarize()

    with open("../../databases/url_to_summary.json", "w") as out:
        json.dump(url_to_summary, out, indent=4)