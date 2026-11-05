import logging
import sqlite3
from langchain_core.retrievers import BaseRetriever
from langchain.tools import tool

from app.helpers.retriever_with_specs import RetrieverWithSpecs

logger = logging.getLogger(__name__)


def create_search_products_tool(retriever: BaseRetriever):

    featuredRetriever = RetrieverWithSpecs(base=retriever)
    
    @tool
    def search_products(query: str):
        """
            Busca productos en el catálogo de hardware (motherboards, procesadores,
            memorias, fuentes, placas de video, etc.) y devuelve sus especificaciones.
            Aquí también puedes encontrar el SKU del producto para identifcarlo dentro de la compañia

            Usala cuando el cliente pregunte por productos, características,
            compatibilidad o pida una recomendación. 

            query: texto en español que describe lo que se busca, con las
            características clave. Ejemplo: "motherboard AM5 con wifi".

            Devuelve una lista numerada de productos; cada uno con su
            descripción, sus specs y su sku. Si no encuentra nada, devuelve
            "Sin resultados."
        """
        try:
            relevant_docs = featuredRetriever.invoke(query)
        except Exception:
            logger.exception("Falló la búsqueda de productos (query=%r)", query)
            raise

        logger.info("search_products(%r): %d documentos recuperados", query, len(relevant_docs))
        if not relevant_docs:
            return "Sin resultados."

        lineas = []
        for numero, doc in enumerate(relevant_docs, start=1):
            lineas.append(f"{numero}. {doc.page_content}")

        return "\n".join(lineas)

    return search_products

def get_connection(db_uri) -> sqlite3.Connection:
        uri = f"{db_uri}?mode=ro"
        conn = sqlite3.connect(uri, uri=True)
        conn.row_factory = sqlite3.Row  # filas accesibles por nombre: row["precio_usd"]
        return conn

def create_price_stock_tool(db_uri):
    
    @tool
    def get_price_and_stock(sku: str):
        """
            Consulta el precio (en USD) y el stock de un producto a partir de su sku.

            sku: código interno del producto, con formato de letras, guion y números
            (ejemplo: "APL-0001"). Nunca lo inventes: obtenelo primero con la tool
            search_products, que lo devuelve junto a cada producto.

            Devuelve el precio y la cantidad en stock, o un aviso si no hay datos
            de ese sku
        """
        db_conn = get_connection(db_uri)
        row = db_conn.execute(
                    "SELECT precio_usd, stock FROM productos WHERE sku = ?",
            (sku.strip().upper(),)
        ).fetchone()
        db_conn.close()
        if row is None:
            return f"El producto {sku} no está disponible"

        if row["stock"] == 0:
            return f"El producto {sku} no está disponible."
        
        return f"El producto {sku} tiene un precio de {row["precio_usd"]} dólares, y tenemos {row["stock"]} disponibles"
    # {"price": row["precio_usd"], "stock": row["stock"]}


    return get_price_and_stock        
        


    