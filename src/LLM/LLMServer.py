from src.LLM import LLM_URL, LOCAL_LLM_PORT, LOCAL_LLM_URL
from flask import Flask, request, jsonify
from flask_cors import CORS
from src.LLM.LLM import *
import requests

class LLMServer:
    
    def __init__(self) -> None:
        self.app = Flask(__name__)
        self.llm = LLM()
        CORS(self.app)
        
    def start(self):
        
        @self.app.route("/", methods=["GET", "POST"])
        def handle_request():
            if request.method == "GET":
                return "Send post request"
            elif request.method == "POST":
                query = request.json["query"]
                content = request.json["content"]

                response = self.llm.generate(query, content)
                response = response.strip()

                data = {"response": response}

                return jsonify(data)


        self.app.run(port=LOCAL_LLM_PORT, debug=True)
        self.llm.model.stop()
            
    def generate_search(self, query, content):
        headers = {"Content-Type": "application/json"}  # Specify JSON content type
        data = {"query": query, "content": content}

        Url = LLM_URL if LLM_URL else LOCAL_LLM_URL

        try:
            response = requests.post(Url, json=data, headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors

            # Assuming the server returns JSON data as well
            generated_text = response.json()
            print("POST request successful")
            print("Response:", generated_text)
            raise Exception("Something went wrong")
            return generated_text

        except requests.exceptions.RequestException as e:
            print(f"POST request failed: {e}")
            raise e.strerror

if __name__ == "__main__":
    llm_server = LLMServer()
    llm_server.start()
    print(f"LLM Server up and running on {LOCAL_LLM_URL}")