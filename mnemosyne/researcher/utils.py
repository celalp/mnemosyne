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
    topic_id: str
    topic_name: str
    topic_description: str
    topic_embeddings: Optional[list] = None
    votes: Optional[dict] = None # the ids of researchers that voted for this topic


@dataclass
class Theme:
    theme_id: str
    theme_name: str
    theme_description: str
    theme_embeddings: Optional[list] = None
    votes: Optional[dict] = None # same as above


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

