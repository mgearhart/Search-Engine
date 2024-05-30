# CS121 Search Engine
## Peter Young, Angela Xiang, David Nguyen, Michael Gearheart

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

### 3. Run `indexer.py`
* this will create the the partitioned index in databases

### 4. Run `run_after_index.py`
* this will create the following json files:
    * `id_to_url.json`
    * `term_to_seek.json`
* this will also create the final index, `final_merged.csv`

### 5. Running the Non-GUI search
* run `search.py` to use the command-line based search

### 6. Running the GUI search
* open a terminal and from the root directory `(Search-Engine)` cd into `web`
* run the backend using `python -m uvicorn gui_main:app --reload` which will launch the backend to your localhost. Wait for the backend to fully load
* once the backend is loaded head over to the web folder and use the VS Code Live Server (or any service to view an html page in a browser) to launch `index.html`. This is the home page
* you can type your query into the search to get your results which will be displayed on `results.html`

### GUI SUMMARY:
* the gui uses a json file called `url_to_summary.json` that contains a mapping of urls to its summary using a local llm (mistral)
* the llm was obtained using the Ollama application more info here: https://ollama.com/
* Github repo for documentation: https://github.com/ollama/ollama
* to generate the summary file go to the web directory and do the following commands--MAKE SURE you system has the hardware to run the LLM:
    * after installing Ollama, go to a terminal and type `ollama run phi3` to download the model. Once downloaded terminate it.
    * go to the web directory and run `llm.py` then wait for the summaries to generate (it will take a long time)



