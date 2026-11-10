import argparse
from pathlib import Path
from dotenv import load_dotenv
from langchain_text_splitters.markdown import MarkdownHeaderTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
import os

parser = argparse.ArgumentParser(description="Ingesta los documentos de politicas en Chroma.")
parser.add_argument(
    "--overwrite",
    action="store_true",
    help="si un archivo ya esta cargado, borra sus chunks y lo vuelve a cargar (por defecto se saltea)",
)
args = parser.parse_args()

folder = Path("data/raw/politicas")
load_dotenv()

embeddings = OpenAIEmbeddings(api_key=os.environ["OPENAI_API_KEY"])
splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("#", "h1"), ("##", "h2")],
        strip_headers=False,    # el titulo queda dentro del texto del chunk
    ) 

vectorstore = Chroma(
    collection_name="politicas",
    embedding_function=embeddings,
    persist_directory="data/chroma_db",
)

def processFile(file):
    data = {}
    content = file.read_text(encoding="utf-8")
    lines = content.split("\n")
    close = lines.index("---", 1)
    for line in lines[1:close]:
        key, _, value = line.partition(":") # "tema: garantia" -> "tema", ":", " garantia"
        data[key.strip()] = value.strip()

    info = "\n".join(lines[close+1:])
    return {"metadata": data, "content": info}


for file in sorted(folder.glob("*.md")):
    data = processFile(file)
    
    chunks = splitter.split_text(data["content"])
    for chunk in chunks:
        chunk.metadata["source"] = file.name
        chunk.metadata.update(data["metadata"])

    loaded = vectorstore.get(where={"source": file.name})["ids"]
    if loaded:
        if not args.overwrite:
            print(f"{file.name}: ya cargado, se saltea (usar --overwrite para reemplazarlo)")
            continue
        vectorstore.delete(ids=loaded)
        print(f"{file.name}: {len(loaded)} chunks borrados")

    vectorstore.add_documents(chunks)
    print(f"{file.name}: {len(chunks)} chunks cargados")


