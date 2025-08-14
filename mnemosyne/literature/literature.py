## most of this code is adapted from https://github.com/ccmbio/ccm_benchmate

import os
from dataclasses import dataclass
from typing import Optional

from bs4 import BeautifulSoup as bs
import requests

from mnemosyne.literature.utils import process_pdf, text_embeddings, image_embeddings

class NoPapersError(Exception):
    pass

class LitSearch:
    def __init__(self, pubmed_api_key=None):
        """
        create the ncessary framework for searching
        :param pubmed_api_key:
        """
        self.pubmed_key = pubmed_api_key

    # TODO advanced search, while technically supported because query is just a string it would be nice if it was explicit
    def search(self, query, database="pubmed", results="id", max_results=1000):
        """
        search pubmed and arxiv for a query, this is just keyword search no other params are implemented at the moment
        :param query: this is a string that is passed to the search, as long as it is a valid query it will work and other fields can be specified
        :param database: pubmed or arxiv
        :param results: what to return, default is paper id PMID and arxiv id
        :param max_results:
        :return: paper ids specific to the database
        """
        # TODO implement pubmed api key for non-free papers
        if database == "pubmed":
            search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={}&retmax={}".format(
                query, max_results)
            search_response = requests.get(search_url)
            search_response.raise_for_status()

            soup = bs(search_response.text, "xml")
            ids = [item.text for item in soup.find_all("Id")]

            if results == "doi":
                dois = []
                for paperid in ids:
                    response = requests.get(
                        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={}".format(paperid))
                    response.raise_for_status()
                    soup = bs(response.text, "xml")
                    dois.append([item.text for item in soup.find_all("ArticleId") if item.attrs["IdType"] == "doi"])
                to_ret = dois
            else:
                to_ret = ids

        elif database == "arxiv":
            search_url = "http://export.arxiv.org/api/search_query?{}&max_results={}".format(query,
                                                                                             str(max_results))
            search_response = requests.get(search_url)
            search_response.raise_for_status()
            soup = bs(search_response.text, "xml")
            ids = [item.text.split("/").pop() for item in soup.find_all("id")][1:]  # first one is the search id
            to_ret = ids
        return to_ret

@dataclass
class PaperData:
    paper_id: str
    id_source: str
    title: Optional[str] | None
    abstract: Optional[str] | None
    abstract_embeddings: Optional[list] | None
    figures: Optional[list] | None
    figure_embeddings: Optional[list] | None
    figure_interpretations: Optional[list] | None
    tables: Optional[list] | None
    table_embeddings: Optional[list] | None
    table_interpretations: Optional[list] | None
    text: Optional[str] | None
    text_chunks: Optional[list] | None # same order as the embeddings
    chunk_embeddings: Optional[list] | None
    download_link: Optional[str] = None
    paper_info: Optional[dict] = None


class Paper:
    def __init__(self, paper_id, id_source, search_info=True):
        self.paper=PaperData(paper_id, id_source)
        #TODO add title to get_abstract
        self.paper.abstract, self.paper.title =self.get_abstract()

        if search_info:
            pass

    def get_abstract(self):
        abstract_text = None
        if self.id_type == "pubmed":
            response = requests.get(
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={}".format(self.paper_id))
            response.raise_for_status()
            soup = bs(response.text, "xml")
            abstract = soup.find("AbstractText")
            if abstract is not None:
                abstract_text = soup.find("AbstractText").text

        elif self.id_type == "arxiv":
            response = requests.get("http://export.arxiv.org/api/query?search_query=id:{}".format(self.paper_id))
            response.raise_for_status()
            soup = bs(response.text, "xml")
            abstract_text = soup.find("summary").text
        else:
            raise NotImplementedError("source must be pubmed or arxiv other sources are not implemented")

        return abstract_text


    def download(self, destination):
        download = requests.get(self.download_link, stream=True)
        download.raise_for_status()
        with open("{}/{}.pdf".format(destination, self.paper_id), "wb") as f:
            f.write(download.content)
        file_paths=os.path.abspath(os.path.join("{}/{}.pdf".format(destination, self.paper_id)))
        self.file_path=file_paths
        return self

    def process(self, file_path, embed_images=True, embed_text=True,
                embed_interpretations=True, **kwargs):
        """
        see utils.py for details
        :return:
        """
        article_text, figures, tables, figure_interpretation, table_interpretation = process_pdf(file_path)
        self.text = article_text
        self.figures = figures
        self.tables = tables
        self.figure_interpretation = figure_interpretation
        self.table_interpretation = table_interpretation

        if embed_images:
            if len(self.figrues) > 0:
                figure_embeddings = []
                for fig in self.figures:
                    figure_embeddings.append(image_embeddings(fig))

            if len(self.tables) > 0:
                table_embeddings = []
                for table in self.tables:
                    table_embeddings.append(embed_images, table)

        if embed_text:
            self.abstract_embeddings = text_embeddings(self.abstract, splitting_strategy="none")[1]
            if self.text is not None:
                self.text_chunks, self.chunk_embeddings = text_embeddings(self.text,
                                                                          splitting_strategy="semantic",
                                                                          **kwargs)
        if embed_interpretations:
            if self.figure_interpretation is not None:
                self.figure_interpretation_embeddings = text_embeddings(self.figure_interpretation,
                                                                        splitting_strategy="none",
                                                                        **kwargs)[1]

            if self.table_interpretation is not None:
                self.table_interpretation_embeddings = text_embeddings(self.table_interpretation,
                                                                       splitting_strategy="none",
                                                                       **kwargs)[1]

        return self

    def __str__(self):
        return self.paper_info["title"]



