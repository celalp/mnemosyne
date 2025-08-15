import os
import time
import subprocess

import openai
import requests
import certifi
import jsonschema
from tqdm import tqdm

#TODO this needs to be refactored currently not compatible with the researcher
class LlamaCppServer:
    def __init__(self, config, binary_path):
        """Initialize Llama.cpp server manager.

        Args:
            binary_path (str): Path to llama.cpp server binary
            model_path (str): Path to the model file
            host (str): Server host (default: localhost)
            port (int): Server port (default: 8080)
        """
        self.current_directory = os.path.abspath(os.getcwd())

        self.binary_path = binary_path
        self.model_dict = config["models"]
        self.host = config["host"]
        self.port = config["port"]
        self.context=config["context_length"]

        cmd = [
            self.model_dict,
            "--host", self.host,
            "--port", str(self.port),
            "--ctx-size", str(self.model_dict["context_length"]),
            "--threads", str(self.model_dict["threads"]),
        ]
        if self.config["ssl_cert"] and self.config["ssl_key"]:
            cmd.extend(["--ssl-cert", self.config["ssl_cert"],
                        "--ssl-key", self.config["ssl_key"]])
            self.protocol="https"
        else:
            self.protocol="http"

        self.process = None
        self.url = f"{self.protocol}://{self.host}:{self.port}"

        # JSON schema for inference output validation
        self.inference_schema = {
            "type": "object",
            "properties": {
                "choices": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "object",
                                "properties": {
                                    "content": {"type": "string"}
                                },
                                "required": ["content"]
                            }
                        },
                        "required": ["message"]
                    }
                }
            },
            "required": ["choices"]
        }

    def start_server(self, model) -> bool:
        """
        start llama.cpp server with a given model
        :param model: model dict from self config
        :return:
        """
        if self.process is not None:
            print("Server is already running")
            return False
        os.chdir(os.path.abspath(self.binary_path))

        model_cmd = ["-m", os.path.abspath(self.model_dict[model]["model"]), "--alias", model]
        cmd=self.cmd.extend(model_cmd)

        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Wait for server to start (with timeout)
            timeout = 30
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    response = requests.get(f"{self.url}/health", verify=certifi.where())
                    if response.status_code == 200:
                        print("Server started successfully")
                        os.chdir(self.current_directory)
                        return True
                except requests.ConnectionError:
                    time.sleep(1)
            print("Server failed to start within timeout")
            self.stop_server()
            os.chdir(self.current_directory)
            return False
        except Exception as e:
            os.chdir(self.current_directory)
            print(f"Failed to start server: {str(e)}")
            return False

    def stop_server(self) -> bool:
        """Stop the Llama.cpp server.

        Returns:
            bool: True if server stopped successfully, False otherwise
        """
        if self.process is None:
            print("No server is running")
            return False

        try:
            self.process.terminate()
            self.process.wait(timeout=10)
            self.process = None
            print("Server stopped successfully")
            return True
        except Exception as e:
            print(f"Failed to stop server: {str(e)}")
            return False

    def single_inference(self, model, note):
        """Run single inference request.

        Args:
            prompt (str): Input prompt
            max_tokens (int): Maximum tokens to generate (default: 512)
            temperature (float): Sampling temperature (default: 0.7)

        Returns:
            Dict: Inference result with validated JSON output
        """
        user_prompt=prepare_prompt(self.model_dict["model"]["prompt"], note)
        messages=[
                    {"role":"system", "content":self.model_dict["system_prompt"]},
                    {"role": "user", "content": user_prompt}
        ]
        client=openai.OpenAI(
            base_url=self.url,
            api_key="key" # not needed for localhost
        )

        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=self.model_dict["model"]["max_tokens"],
                temperature=self.model_dict["model"]["temperature"],
                stream=False
            )
            result = response.to_dict()

            # Validate JSON schema
            jsonschema.validate(instance=result, schema=self.inference_schema)

            # Simplify output to {"summary_text": <text>} format
            simplified_result = result["choices"][0]["message"]["content"]
            return simplified_result

        except (openai.APIError, jsonschema.ValidationError) as e:
            return {"error": f"Inference failed: {str(e)}"}

    def batch_inference(self, model, notes):
        """Run batch inference requests.

        Args:
            prompts (List[str]): List of input prompts
            max_tokens (int): Maximum tokens to generate (default: 512)
            temperature (float): Sampling temperature (default: 0.7)

        Returns:
            List[Dict]: List of inference results with validated JSON output
        """
        results = []
        for note in tqdm(notes, unit=" Notes", desc="Processing: "):
            result = self.single_inference(model, note)
            results.append(result)
        return results

    def is_server_running(self):
        """Check if the server is running.

        Returns:
            bool: True if server is running, False otherwise
        """

        response = requests.get(f"{self.url}/health", verify=certifi.where())
        return response.status_code == 200

class ModelServe:
    """
    this will contain a few methods to serve or connnect to models,
    the main types will be via llamacpp, huggingface and other closed source models
    """