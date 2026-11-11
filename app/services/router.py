import re

from langchain_core.messages import get_buffer_string


router_prompt = """Clasificá el último mensaje del cliente en UNA categoría:
- sales: pregunta por precio, costo, stock, disponibilidad, si hay, o quiere comprar. Sobre hardware (especificaciones, caracteristicas, compatibilidad, recomendaciones, comparaciones).
- policies: preguntas acerca de garantía, envíos de productos, cambios y devoluciones (devolver) de productos por cualquier motivo, medios de pago, productos importados, servicio técnico, dirección y horarios. También información sobre la empresa Prompt Hardware: quiénes son, historia, equipo, contacto, redes, el asistente Clippo.
Usá el historial para entender mensajes cortos, dando mas relevancia a ultimos mensajes, como "¿y cuánto sale?".
Respondé solo con una palabra: "sales" o "policies". Siempre esas 2 opciones. NO las traduzcas"""

class AgentRouter:

    POLICY_WORDS = {"garantia", "envio", "envios", "devolucion", "devolver", "reembolso", "politica", "politicas", "horario", "horarios", "quienes", "empresa", "compania", "historia", "contacto", "telefono", "direccion"}
    SALES_WORDS = {"precio", "cuesta", "cuanto", "stock", "disponible", "disponibilidad", "comprar"}

    
    def wordSetDecomposition(self, query: str):
        normalized = query.lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
        return set(re.findall(r"\w+", normalized))

    def __init__(self, llm=None):
        self.llm = llm
    
    def _by_rules(self, userPrompt: str):
        words = self.wordSetDecomposition(userPrompt)
        salesCount = len(words & self.SALES_WORDS)
        policyCount = len(words & self.POLICY_WORDS)

        if (salesCount > policyCount):
            return "sales"
        elif (policyCount > salesCount):
            return "policies"

        return None

    def _by_llm(self, userPrompt: str, memory):
        try:
            history = memory.load_memory_variables({})["chat_history"]
            context = get_buffer_string(history[-4:])
            message = context + "\nHuman: " + userPrompt
            response = self.llm.invoke([("system", router_prompt), ("human", message)])
            print(f"-------------------------------------- {response.content} ----------")
            return response.content.lower()
        except Exception as e:
            print(e)
            return None
            
    def route(self, userPrompt, memory):
        agent = self._by_rules(userPrompt=userPrompt)
        if (not agent):
            agent = self._by_llm(userPrompt=userPrompt,memory=memory)

        if (not agent):
            return 'sales'

        return agent

        