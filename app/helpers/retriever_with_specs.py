from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document

class RetrieverWithSpecs(BaseRetriever):
    base: BaseRetriever          # tu retriever actual

    def _get_relevant_documents(self, query, *, run_manager=None):
        docs = self.base.invoke(query)       # busca igual que antes
        resultado = []
        for d in docs:
            specs = " | ".join(f"{k}: {v}" for k, v in d.metadata.items())
            resultado.append(Document(page_content=f"{d.page_content} | {specs}",
                                      metadata=d.metadata))
        return resultado