# CS121 Search Engine
## Peter Young, Angela Xiang, David Nguyen, Michael Gearhart

## Running the Search Engine:
### 1. Install prerequisites
* `pip install bs4`
* `pip install nltk`
* `pip install requests`
* Backend for gui:
    * `pip install fastapi`
    * `pip install uvicorn`
* Frontend for gui:
    * VS Code live server

### 2. Load auxillary directory
* make a directory called databases with the parent directory being Search-Engine

### 3. Run `pipeline.py`
* input '12345678' in the commandline to fully index everything. You can do it in batches, like '1' first,
* then run again with '2', but make sure it's in order.

### 4. Running the Non-GUI search
* run 'ranked_search.py', which lets you input searches, and outputs urls relevant to the query

### 5. Running the GUI search
* open a terminal and from the root directory `(Search-Engine)` cd into `web`
* run the backend using `python -m uvicorn gui_main:app --reload` which will launch the backend to your localhost. Wait for the backend to fully load
* once the backend is loaded head over to the web folder and use the VS Code Live Server (or any service to view an html page in a browser) to launch `index.html`. This is the home page
* you can type your query into the search to get your results which will be displayed on `results.html`

### GUI SUMMARY:
* the gui uses 4 json files called `cleaned_id_to_summary_part[1234].json` that contains a mapping of urls to its summary using a local llm (phi3)
* the llm was obtained using the Ollama application more info here: https://ollama.com/
* Github repo for documentation: https://github.com/ollama/ollama
* to generate the summary file go to the web directory and do the following commands--MAKE SURE you system has the hardware to run the LLM:
    * after installing Ollama, go to a terminal and type `ollama run phi3` to download the model. Once downloaded terminate it.
    * prepare `id_to_url.json` by creating a new file called `urlChunks` in the `databases` directory
        * go to web/scripts and run chunkurl.py to split the json file
    * in the same directory run `llm.py` changing the path of the json file each time then wait for the summaries to generate (it will take a long time)



