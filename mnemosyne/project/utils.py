from typing import List
import io

from sqlalchemy import select, insert
from PIL import Image
import torch

from mnemosyne.literature.literature import Paper, PaperInfo, LitSearch

class DataIntegrityError(Exception):
    pass

class ProjectNameError(Exception):
    pass

class NotFoundError(Exception):
    pass


def add_papers(project, papers: List[Paper]):
    """This will add a list of paper class instances and if not a paper class instance or does not have a paperinfo dataclass will raise an error"""
    papers_table=project.kb.db_tables["papers"]
    authors_table=project.kb.db_tables["authors"]
    figures_table=project.kb.db_tables["figures"]
    tables_table=project.kb.db_tables["tables"]
    body_text_table=project.kb.db_tables["body_text"]
    chunked_text_table=project.kb.db_tables["body_text_chunked"]
    references_table = project.kb.db_tables["references"]
    related_works_table = project.kb.db_tables["related_works"]
    cited_by_table = project.kb.db_tables["cited_by"]

    for item in papers:
        if isinstance(item, Paper):
            if isinstance(item.info, PaperInfo):
                stms=insert(papers_table.c.source_id, papers.c.source, papers.c.title,
                            papers.c.project_id,
                            papers.c.abstract, papers.c.abstract_embeddings,
                            papers.c.pdf_url, papers.c.pdf_path,
                            papers.c.openalex_response).values(item.info.id, item.info.id_type,
                                                               item.info.title,
                                                               project.project_id,
                                                               item.info.abstract,
                                                               item.info.abstract_embeddings,
                                                               item.info.download_link,
                                                               item.info.pathname,
                                                               item.info.openalex_info).returning(papers_table.c.paper_id)
                paper_id=project.kb.session().execute(stms).scalar()

                for author in item.info.authors: #TODO need to check if already in db
                    author_stms=insert(authors_table.c.paper_id,
                                      authors_table.c.name,
                                      author.c.affiliation).values(paper_id,
                                                                   author["name"],
                                                                   author["affiliation"])
                    project.kb.session().execute(author_stms)

                if item.info.figures is not None:
                    for i in range(len(item.info.figures)):
                        img = Image.open(item.info.figures[i])
                        img_byte_arr = io.BytesIO()
                        img.save(img_byte_arr, format="JPEG")
                        img_bytes = img_byte_arr.getvalue()
                        figure_stms=insert(figures_table.c.paper_id, figures_table.c.image_blob,
                                           figures_table.c.ai_caption,
                                           figures_table.c.figure_embeddings,
                                           figures_table.c.figure_interpretation_embeddings).values(paper_id,
                                                                                     img_bytes,
                                                                                     item.info.figure_interpretation[i],
                                                                                     item.info.figure_embeddings[i],
                                                                                     item.info.figure_interpretation_embeddings[i]
                                                                                     )
                        project.kb.session().execute(figure_stms)

                if item.info.tables is not None:
                    for i in range(len(item.info.tables)):
                        img = Image.open(item.info.tables[i])
                        img_byte_arr = io.BytesIO()
                        img.save(img_byte_arr, format="JPEG")
                        img_bytes = img_byte_arr.getvalue()
                        table_smts = insert(tables_table.c.paper_id, tables_table.c.image_blob,
                                             tables_table.c.ai_caption,
                                             tables_table.c.table_embeddings,
                                             tables_table.c.table_interpretation_embeddings).values(paper_id,
                                                                                       img_bytes,
                                                                                       item.info.table_interpretation[i],
                                                                                       item.info.table_embeddings[i],
                                                                                       item.info.table_interpretation_embeddings[i]
                                                                                       )
                        project.kb.session().execute(table_smts)

                if item.info.text is not None:
                    text_stms=insert(body_text_table.c.paper_id, body_text_table.c.text,).values(paper_id, item.info.text)
                    project.kb.session().execute(text_stms)

                if item.info.text_chunks is not None:
                    for i in range(len(item.info.text_chunks)):
                        chunk_stms=insert(chunked_text_table.c.paper_id, chunked_text_table.c.chunk,
                                          chunked_text_table.c.chunk_embeddings).values(paper_id,
                                                                                       item.info.text_chunks[i],
                                                                                       item.info.chunk_embeddings[i])
                        project.kb.session().execute(chunk_stms)

                if item.info.references is not None:
                    for paper in item.info.references:
                        existing=select(papers_table.c.paper_id).where(papers_table.c.source_id==paper.info.id, papers_table.c.id_type==paper.info.id_type)
                        ref_id=project.kb.session().execute(existing).scalar()
                        if ref_id is None:
                            ref_id=project.add_papers(paper)
                        stms=insert(references_table.c.paper_id, references_table.c.id,).values(paper_id, ref_id)
                        project.kb.session().execute(stms)

                if item.info.related_works is not None:
                    for paper in item.info.related_works: #
                        existing = select(papers_table.c.paper_id).where(papers_table.c.source_id == paper.info.id,
                                                                         papers_table.c.id_type == paper.info.id_type)
                        related_id = project.kb.session().execute(existing).scalar()
                        if related_id is None:
                            related_id = project.add_papers(paper)
                        stms = insert(related_works_table.c.paper_id, related_works_table.c.id, ).values(paper_id, related_id)
                        project.kb.session().execute(stms)

                if item.info.cited_by is not None:
                    for paper in item.info.cited_by:
                        existing = select(papers_table.c.paper_id).where(papers_table.c.source_id == paper.info.id,
                                                                         papers_table.c.id_type == paper.info.id_type)
                        cited_id = project.kb.session().execute(existing).scalar()
                        if cited_id is None:
                            cited_id = project.add_papers(paper)
                        stms = insert(cited_by_table.c.paper_id, cited_by_table.c.id, ).values(paper_id, cited_id)
                        project.kb.session().execute(stms)

                project.kb.session().commit()

            else:
                raise ValueError("Paper instance must have a PaperInfo instance")
        else:
            raise TypeError("All items in the papers list must be of type Paper")

    return None

def get_paper(project, id):
    papers_table=project.kb.db_tables["papers"]
    authors_table=project.kb.db_tables["authors"]
    figures_table=project.kb.db_tables["figures"]
    tables_table=project.kb.db_tables["tables"]
    body_text_table=project.kb.db_tables["body_text"]
    chunked_text_table=project.kb.db_tables["body_text_chunked"]
    references_table = project.kb.db_tables["references"]
    related_works_table = project.kb.db_tables["related_works"]
    cited_by_table = project.kb.db_tables["cited_by"]

    selection = select(
        papers_table.c.source_id,
        papers_table.c.source,
        papers_table.c.title,
        papers_table.c.abstract,
        papers_table.c.abstract_embeddings,
        papers_table.c.text,
        papers_table.c.pdf_url,
        papers_table.c.pdf_path,
        papers_table.c.openalex_response,
    ).where(papers_table.c.paper_id == id)
    paper_info=project.kb.session().execute(selection).fetchall()

    if len(paper_info) > 1:
        raise DataIntegrityError("Paper id/source combination is not unique")
    elif len(paper_info)==0:
        raise NotFoundError("Paper id/source combination not found")
    else:
        paper=Paper(paper_id=paper_info[0][0], id_type=paper_info[0][1], get_abstract=False)
        paper.info.title=paper_info[0][2]
        paper.info.abstract=paper_info[0][3]
        paper.info.abstract_embeddings=paper_info[0][4]
        paper.info.text=paper_info[0][5]
        paper.info.download_link=paper_info[0][6]
        paper.info.file_path=paper_info[0][7]
        if paper.info.file_path is not None:
            paper.info.downloaded=True
        else:
            paper.info.downloaded=False
        paper.info.openalex_response=paper_info[0][8]

    authors=select(authors_table.c.name, authors_table.c.affiliation).where(authors_table.c.paper_id==id)
    authors=project.kb.session().execute(authors).fetchall()
    paper.info.authors=[]
    for author in authors:
        auth={}
        auth["name"]=author[0]
        auth["affiliation"]=author[1]
        paper.info.authors.append(auth)

    figures=select(figures_table.c.image_blob,
                   figures_table.c.figure_embeddings,
                   figures_table.c.ai_caption,
                   figures_table.c.figure_interpretation_embeddings).where(figures_table.c.paper_id==id)
    figures=project.kb.session().execute(figures).fetchall()
    if len(figures)==0:
        paper.info.figures=None
    else:
        paper.info.figures=[Image(figure[0]) for figure in figures]
        paper.info.figure_embeddings=[figure[1] for figure in figures]
        paper.info.figure_interpretation=[figure[2] for figure in figures]
        paper.info.figure_interpretation_embeddings=[figure[3] for figure in figures]

    tables=select(tables_table.c.image_blob,
                  tables_table.c.table_embeddings,
                  tables_table.c.ai_caption,
                  tables_table.c.table_interpretation_embeddings).where(tables_table.c.paper_id==id)
    tables=project.kb.session().execute(tables).fetchall()
    if len(tables)==0:
        paper.info.tables=None
    else:
        paper.info.tables = [Image(table[0]) for table in tables]
        paper.info.table_embeddings = [table[1] for table in tables]
        paper.info.table_interpretation = [table[2] for table in tables]
        paper.info.table_interpretation_embeddings = [table[3] for table in tables]


    chunks=select(chunked_text_table.c.chunk,
                  chunked_text_table.c.chunk_embeddings).where(chunked_text_table.c.paper_id==id)
    chunks=project.kb.session().execute(chunks).fetchall()
    if len(chunks)==0:
        paper.info.text_chunks=None
    else:
        paper.info.text_chunks=[chunk[0] for chunk in chunks]
        paper.info.chunk_embeddings=[chunk[1] for chunk in chunks]

    references=select(references_table.c.target_id).where(references_table.c.paper_id==id)
    references=project.kb.session().execute(references).fetchall()
    if len(references)==0:
        paper.info.references=None
    else:
        refs=[]
        for ref in references:
            ref_paper=get_paper(project, ref[1])
            refs.append(ref_paper)
        paper.info.references=refs

    cited_by=select(cited_by_table.c.target_id).where(cited_by_table.c.paper_id==id)
    cited_by=project.kb.session().execute(cited_by).fetchall()
    if len(cited_by)==0:
        paper.info.cited_by=None
    else:
        refs=[]
        for ref in cited_by:
            ref_paper=get_paper(project, ref[1])
            refs.append(ref_paper)
        paper.info.cited_by=refs

    related_works=select(related_works_table.c.target_id).where(related_works_table.c.paper_id==id)
    related_works=project.kb.session().execute(related_works).fetchall()
    if len(related_works)==0:
        paper.info.related_works=None
    else:
        refs=[]
        for ref in related_works:
            ref_paper=get_paper(project, ref[1])
            refs.append(ref_paper)
        paper.info.related_works=refs

    return paper

def keyword_search():
    pass

# given a figure (or caption) find similar figures in the knowledgebase
def figure_search():
    pass

def embedding_search():
    pass

def search():
    pass