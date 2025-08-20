from dataclasses import dataclass
from typing import Optional

@dataclass
class Topic:
    """
    This is the topic class, it is used to store the topic information and also the topic embeddings, the topics are a low
    level annotation of the data that is being analyzed the first step is to come up with topics

    then the researchers vote for the topics and the topic and then they are decided by the manages,

    once the topics are decided then the researchers will vote on themes and how topcis can be grouped into themes
    """
    topic_name: str
    topic_description: str
    topic_chunk: Optional[str] = None
    topic_embeddings: Optional[list] = None

@dataclass
class Theme:
    theme_name: str
    theme_description: str
    theme_topics: Optional[list] = None
    theme_embeddings: Optional[list] = None

def generate_prompt(base_prompt, project_description, topicset, abstracts=None):
    """
    Generate the prompt for the researcher, these include the base prompt, the project description, from the project metaclass
    the topicset that is selected randomly and the abstracts. Abstracts are collected by the researcher itself and
    are then added to the prompt.The model will then be re-initialized.
    are then added to the prompt.The model will then be re-initialized.
    :param base_prompt:
    :param project_description:
    :param topicset:
    :param abstracts:
    :return:
    """
    return "\n".join([base_prompt, project_description, topicset])


def clusters(embeddings, algorithm="dbscan"):
    """
    this is a quicker way to group things, rather than researchers fighting it out, we are going to take the embeddings
    of topics, or themes, or data segmented chunks, we can also do this with the model reasonings to see if the models are on the
    same page on some of the clusters.
    :param embeddings:
    :param algorithm:
    :return:
    """
    pass


