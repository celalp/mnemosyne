
# currently we are only supporting HuggingFace models
from transformers import AutoModelForCausalLM, AutoTokenizer

from mnemosyne.researcher.utils import *

class Researcher:
    def __init__(self, name, description, model_name, cache_dir):
        self.name=name
        self.description=description
        self.model_name=model_name
        self.cache_dir=cache_dir
        self.prompt=None
        self.model=None
        self.tokenizer=None
        self.themes=None
        self.topics=None
        self.papers=None

    def load(self):
        model=AutoModelForCausalLM.from_pretrained(self.model_name, cache_dir=self.cache_dir)
        tokenizer=AutoTokenizer.from_pretrained(self.model_name, cache_dir=self.cache_dir)
        self.model=model
        self.tokenizer=tokenizer

    def vote_on_paper(self, paper_id):
        pass

    def vote_on_theme(self, theme, chunk):
        pass

    def vote_on_topic(self, topic, chunk):
        pass

    def create_topic(self, topic):
        pass

    def create_theme(self, theme):
        pass


class Manager(Researcher):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def decide(self, themes=None, topics=None, papers=None,):
        pass