
# currently we are only supporting HuggingFace models

import openai

from mnemosyne.researcher.model_serve import LlamaCppModel, HFModel, ClosedModel
from mnemosyne.literature.literature import PaperInfo, Paper
from mnemosyne.researcher.utils import *


class Researcher:
    def __init__(self, name, description, prompt, interests):
        """
        Instantiate a researcher, each researcher should have a uniqute name and a comprehensive description about how they
        are going to be involved in the research. They should have a list of interests that is overlapping the the overall
        project goals thare listed in the mnemosyne.project.project.Project class instance.
        :param name: name of the model
        :param description: description of the researcher, this should resemble an actual researchers intro page
        :param prompt: this is a basic system prompt that will be used to generate the prompt for the researcher
        :param interests: list of strings to specify what the researcher is interested in
        """
        self.name=name
        self.description=description
        self.prompt=prompt
        if isinstance(interests, str):
            self.interests=[interests]
        else:
            self.interests=interests
        self.model=None

    def load(self, type="huggingface", **kwargs):
        if type=="huggingface":
            self.model=HFModel(**kwargs)
        elif type=="llamacpp":
            self.model=LlamaCppModel(**kwargs)
        else:
            self.model=ClosedModel(**kwargs)

    #TODO come up with a way to include all the responsibilities of the researcher
    def assign_topics(self, chunk):
        pass

    def assign_themes(self, topics):
        pass

    def pick_papers(self, paperlist):
        pass

    def read_papers(self, papers):
        pass




class Manager(Researcher):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def decide(self, themes=None, topics=None, papers=None,):
        pass