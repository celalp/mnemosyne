import os
import time
import subprocess

import openai
import requests
import certifi
import jsonschema
from tqdm import tqdm

from torch.cuda import is_available
from transformers import AutoModelForCausalLM, AutoTokenizer

from mnemosyne.researcher.utils import *

# these are classes that represent different types of models to be served, they will all have a call method that will
# Hopefully return the desired output


class HFModel:
    def __init__(self, model_name, sys_prompt, **kwargs):
        self.model_name=model_name
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name, **kwargs)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, **kwargs)
        self.messages = [{"role": "system", "content": sys_prompt},
                    {"role":"user", "content": ""}]
        self.device = "cuda" if is_available() else "cpu"

    def call(self, user_prompt):
        messages = self.messages.copy()
        messages[1]["content"]=user_prompt
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.device)

        # conduct text completion
        generated_ids = self.model.generate(
            **model_inputs,
            max_new_tokens=500
        )
        output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()

        content = self.tokenizer.decode(output_ids, skip_special_tokens=True)
        return content

class LlamaCppModel:
    def __init__(self, config, binary_path):
        """
        #TODO a very detailed description of the model and the config with an example
        :param config:
        :param binary_path:
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

    def single_inference(self, model, sys_prompt, user_prompt,):
        """Run single inference request.

        Args:
            prompt (str): Input prompt
            max_tokens (int): Maximum tokens to generate (default: 512)
            temperature (float): Sampling temperature (default: 0.7)

        Returns:
            Dict: Inference result with validated JSON output
        """
        messages=[
                    {"role":"system", "content":sys_prompt},
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

    def call(self, model, notes):
        """Run batch inference requests.

        Args:
            prompts (List[str]): List of input prompts
            max_tokens (int): Maximum tokens to generate (default: 512)
            temperature (float): Sampling temperature (default: 0.7)

        Returns:
            List[Dict]: List of inference results with validated JSON output
        """
        if isinstance(notes, str):
            notes = [notes]

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

class ClosedModel:
    def __init__(self, url, sys_prompt, api_key=None, name=None):
        self.url=url
        self.api_key=api_key
        self.name=name

        self.client=openai.OpenAI(
            api_key=api_key,
            base_url=url
        )
        self.messages = [{"role": "system", "content": sys_prompt},
                         {"role": "user", "content": ""}]

    def call(self, prompt, **kwargs):
        messages = self.messages.copy()
        messages[1]["content"]=prompt
        response=self.client.chat.completions.create(
            model=self.name,
            messages=messages,
            **kwargs #for model specific stuff like tempreature max tokens etc.
        )
        return response.choices[0].message.content

