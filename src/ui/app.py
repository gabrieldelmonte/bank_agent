"""
Main Streamlit UI for Bank Agent System.

This is the user interface for interacting with the banking agents.
"""

import streamlit as st
import os
import sys
from datetime import datetime

# Add the parent directory (src) to the path so we can import agents
src_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, src_path)

from agents.triagem import TriagemAgent
from agents.credito import CreditoAgent
from agents.entrevista_credito import EntrevistaCreditoAgent
from agents.cambio import CambioAgent


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if "triagem_agent" not in st.session_state:
        st.session_state.triagem_agent = TriagemAgent()
    if "credito_agent" not in st.session_state:
        st.session_state.credito_agent = CreditoAgent()
    if "entrevista_agent" not in st.session_state:
        st.session_state.entrevista_agent = EntrevistaCreditoAgent()
    if "cambio_agent" not in st.session_state:
        st.session_state.cambio_agent = CambioAgent()

    if "current_agent" not in st.session_state:
        st.session_state.current_agent = "triagem"
    if "authenticated_client" not in st.session_state:
        st.session_state.authenticated_client = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Add initial greeting
        greeting = st.session_state.triagem_agent.send_message(
            "Faça uma saudação inicial amigável e bem-vinda ao cliente do Banco Ágil."
        )
        st.session_state.messages.append({"role": "assistant", "content": greeting})
    if "waiting_for" not in st.session_state:
        st.session_state.waiting_for = "cpf"
    if "temp_cpf" not in st.session_state:
        st.session_state.temp_cpf = None
    if "interview_step" not in st.session_state:
        st.session_state.interview_step = 0
    if "last_agent_question" not in st.session_state:
        st.session_state.last_agent_question = None


def get_current_agent():
    """Get the current active agent."""
    if st.session_state.current_agent == "triagem":
        return st.session_state.triagem_agent
    elif st.session_state.current_agent == "credito":
        return st.session_state.credito_agent
    elif st.session_state.current_agent == "entrevista":
        return st.session_state.entrevista_agent
    elif st.session_state.current_agent == "cambio":
        return st.session_state.cambio_agent
    return st.session_state.triagem_agent


def switch_agent(new_agent: str):
    """Switch to a different agent."""
    if st.session_state.current_agent != new_agent:
        st.session_state.current_agent = new_agent


def process_user_message(user_input: str):
    """Process user message and generate agent response."""
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    agent = get_current_agent()
    
    # Handle authentication flow
    if st.session_state.current_agent == "triagem" and not st.session_state.authenticated_client:
        if st.session_state.waiting_for == "cpf":
            # Validate CPF
            cpf = user_input.replace("-", "").replace(".", "").strip()
            if len(cpf) == 11 and cpf.isdigit():
                st.session_state.temp_cpf = cpf
                st.session_state.waiting_for = "dob"
                response = agent.send_message(
                    f"O cliente informou o CPF {cpf}. Peça agora a data de nascimento no formato YYYY-MM-DD."
                )
            else:
                response = agent.send_message(
                    f"O cliente informou um CPF inválido: '{user_input}'. Explique que o CPF deve ter 11 dígitos e peça novamente."
                )
        
        elif st.session_state.waiting_for == "dob":
            # Validate date of birth
            dob = user_input.strip()
            if len(dob) == 10 and dob.count("-") == 2:
                # Try to authenticate
                if agent.authenticate_client(st.session_state.temp_cpf, dob):
                    client = agent.get_authenticated_client()
                    st.session_state.authenticated_client = client
                    st.session_state.credito_agent.set_client(client)
                    st.session_state.entrevista_agent.set_client(client)
                    st.session_state.waiting_for = None
                    response = agent.send_message(
                        f"Autenticação bem-sucedida! Cliente: {client.get('nome')}. Pergunte como pode ajudar hoje e mencione as opções: consultar limite, aumentar limite, entrevista de crédito ou consultar câmbio."
                    )
                else:
                    agent.increment_attempts()
                    attempts_left = agent.max_attempts - agent.get_authentication_attempts()
                    if agent.is_max_attempts_reached():
                        response = "❌ Falha na autenticação após 3 tentativas. Por segurança, o atendimento foi encerrado. Por favor, entre em contato com a agência."
                        st.session_state.waiting_for = "finished"
                    else:
                        st.session_state.waiting_for = "cpf"
                        st.session_state.temp_cpf = None
                        response = agent.send_message(
                            f"Autenticação falhou. O cliente tem {attempts_left} tentativa(s) restante(s). Peça o CPF novamente de forma educada."
                        )
            else:
                response = agent.send_message(
                    f"Data inválida: '{user_input}'. Explique que a data deve estar no formato YYYY-MM-DD (ex: 1990-01-15) e peça novamente."
                )
    
    # Handle authenticated user requests
    elif st.session_state.authenticated_client:
        user_lower = user_input.lower()
        
        # Check if user wants to exit (highest priority)
        if any(word in user_lower for word in ["sair", "encerrar", "tchau", "obrigado e sair", "finalizar", "até logo", "ate logo", "adeus"]):
            agent = get_current_agent()
            response = agent.send_message(
                "O cliente quer encerrar o atendimento. Agradeça de forma cordial, deseje um ótimo dia e mencione que o Banco Ágil está sempre à disposição."
            )
            st.session_state.waiting_for = "finished"
        
        # Check if user is answering yes/no to a previous question
        elif any(word in user_lower for word in ["sim", "yes", "quero", "gostaria", "pode"]) and st.session_state.last_agent_question == "limit_increase_offer":
            # User confirmed they want to increase limit
            switch_agent("credito")
            agent = get_current_agent()
            st.session_state.waiting_for = "limit_value"
            st.session_state.last_agent_question = None
            response = agent.send_message(
                "O cliente confirmou que quer aumentar o limite. Pergunte qual o novo valor de limite desejado em reais de forma clara e objetiva."
            )
        
        # First check if user is providing a value for limit increase (handles both direct request with value)
        elif st.session_state.waiting_for == "limit_value":
            # Extract numeric value from input
            try:
                # Remove currency symbols and extract number
                value_str = user_input.replace("R$", "").replace(".", "").replace(",", ".").strip()
                # Try to extract just numbers
                import re
                numbers = re.findall(r'\d+\.?\d*', value_str)
                if numbers:
                    requested_limit = float(numbers[0])
                else:
                    raise ValueError("No number found")
                
                if requested_limit > 0:
                    credito_agent = st.session_state.credito_agent
                    result = credito_agent.create_limit_increase_request(requested_limit)
                    status = result.get("status", "erro")
                    mensagem = result.get("mensagem", "")
                    
                    if status == "aprovado":
                        st.session_state.authenticated_client["limite_credito"] = str(requested_limit)
                        st.session_state.waiting_for = None
                        st.session_state.last_agent_question = None
                        st.session_state.current_agent = "credito"
                        agent = get_current_agent()
                        response = agent.send_message(
                            f"Solicitação aprovada! {mensagem}. Informe ao cliente de forma entusiasmada e pergunte se precisa de mais alguma coisa."
                        )
                    elif status == "rejeitado":
                        st.session_state.waiting_for = None
                        st.session_state.last_agent_question = None
                        st.session_state.current_agent = "credito"
                        agent = get_current_agent()
                        response = agent.send_message(
                            f"Solicitação rejeitada. {mensagem}. Ofereça realizar uma entrevista de crédito para tentar melhorar o score."
                        )
                    else:
                        st.session_state.waiting_for = None
                        st.session_state.last_agent_question = None
                        st.session_state.current_agent = "credito"
                        agent = get_current_agent()
                        response = agent.send_message(
                            f"Erro ao processar solicitação: {mensagem}. Pergunte se deseja tentar novamente."
                        )
                else:
                    agent = get_current_agent()
                    response = agent.send_message(
                        "Valor inválido. Peça ao cliente um valor positivo em reais."
                    )
            except (ValueError, IndexError):
                agent = get_current_agent()
                response = agent.send_message(
                    f"Não consegui identificar o valor em '{user_input}'. Peça ao cliente para informar apenas o valor numérico em reais (ex: 8000 ou 8.000)."
                )
        
        # Check if waiting for currency input (high priority - before keyword matching)
        elif st.session_state.waiting_for == "from_currency":
            agent = get_current_agent()
            from_curr = user_input.upper().strip()
            # Extract 3-letter currency code
            currencies = st.session_state.cambio_agent.get_common_currencies()
            found_curr = None
            for code in currencies.keys():
                if code in from_curr:
                    found_curr = code
                    break
            
            if found_curr:
                st.session_state.temp_from_currency = found_curr
                st.session_state.waiting_for = "to_currency"
                response = agent.send_message(
                    f"Entendido, {found_curr}. Pergunte agora para qual moeda deseja converter (BRL, USD, EUR, etc)."
                )
            else:
                response = agent.send_message(
                    f"Moeda '{user_input}' não reconhecida. Peça uma moeda válida: USD, EUR, GBP, JPY, AUD, CAD, CHF, CNY, INR, BRL."
                )
        
        elif st.session_state.waiting_for == "to_currency":
            agent = get_current_agent()
            to_curr = user_input.upper().strip()
            currencies = st.session_state.cambio_agent.get_common_currencies()
            found_curr = None
            for code in currencies.keys():
                if code in to_curr:
                    found_curr = code
                    break
            
            if found_curr:
                from_curr = st.session_state.temp_from_currency
                exchange_data = st.session_state.cambio_agent.get_exchange_rate(from_curr, found_curr)
                formatted_response = st.session_state.cambio_agent.format_exchange_response(exchange_data)
                st.session_state.waiting_for = None
                st.session_state.last_agent_question = None
                st.session_state.current_agent = "cambio"
                agent = get_current_agent()
                response = agent.send_message(
                    f"Consulta de {from_curr} para {found_curr}. Informe: {formatted_response}. Pergunte se deseja outra consulta ou algo mais."
                )
            else:
                response = agent.send_message(
                    f"Moeda '{user_input}' não reconhecida. Peça uma moeda válida: USD, EUR, GBP, JPY, AUD, CAD, CHF, CNY, INR, BRL."
                )
        
        # Check for cambio BEFORE credit limit to avoid false matches
        elif any(word in user_lower for word in ["câmbio", "cambio", "cotação", "cotacao", "moeda", "dolar", "dólar", "euro", "taxa", "taxas", "conversão"]):
            switch_agent("cambio")
            agent = get_current_agent()
            st.session_state.waiting_for = "from_currency"
            st.session_state.last_agent_question = None
            response = agent.send_message(
                "O cliente quer consultar câmbio. Pergunte de qual moeda ele deseja consultar (USD, EUR, GBP, JPY, etc)."
            )
        
        # Check what user wants
        elif any(word in user_lower for word in ["limite", "consultar", "ver limite", "meu limite"]) and "aumentar" not in user_lower and "aumento" not in user_lower and "câmbio" not in user_lower and "cambio" not in user_lower:
            switch_agent("credito")
            agent = get_current_agent()
            
            limit_info = agent.get_client_credit_limit()
            st.session_state.last_agent_question = "limit_increase_offer"
            response = agent.send_message(
                f"O cliente quer saber o limite. Informe: {limit_info}. Pergunte de forma clara e direta se deseja solicitar um aumento."
            )
        
        elif any(word in user_lower for word in ["aumentar", "aumento", "solicitar"]) and any(word in user_lower for word in ["limite", "credito", "crédito"]):
            switch_agent("credito")
            agent = get_current_agent()
            
            # Check if user already provided a value in the same message
            import re
            numbers = re.findall(r'\d+\.?\d*', user_input.replace(".", "").replace(",", "."))
            if numbers and len(numbers) > 0:
                # User provided value directly, process it
                try:
                    requested_limit = float(numbers[0])
                    if requested_limit > 100:  # Reasonable limit value
                        st.session_state.waiting_for = "limit_value"
                        # Process immediately by calling the same logic
                        result = agent.create_limit_increase_request(requested_limit)
                        status = result.get("status", "erro")
                        mensagem = result.get("mensagem", "")
                        
                        if status == "aprovado":
                            st.session_state.authenticated_client["limite_credito"] = str(requested_limit)
                            st.session_state.waiting_for = None
                            st.session_state.last_agent_question = None
                            st.session_state.current_agent = "credito"
                            agent = get_current_agent()
                            response = agent.send_message(
                                f"Solicitação de R$ {requested_limit:.2f} aprovada! {mensagem}. Informe ao cliente de forma entusiasmada e pergunte se precisa de mais alguma coisa."
                            )
                        elif status == "rejeitado":
                            st.session_state.waiting_for = None
                            st.session_state.last_agent_question = None
                            st.session_state.current_agent = "credito"
                            agent = get_current_agent()
                            response = agent.send_message(
                                f"Solicitação de R$ {requested_limit:.2f} rejeitada. {mensagem}. Ofereça realizar uma entrevista de crédito para tentar melhorar o score."
                            )
                        else:
                            st.session_state.waiting_for = None
                            st.session_state.last_agent_question = None
                            st.session_state.current_agent = "credito"
                            agent = get_current_agent()
                            response = agent.send_message(
                                f"Erro ao processar solicitação: {mensagem}. Pergunte se deseja tentar novamente."
                            )
                    else:
                        raise ValueError("Value too low")
                except (ValueError, IndexError):
                    st.session_state.waiting_for = "limit_value"
                    response = agent.send_message(
                        "O cliente quer aumentar o limite. Pergunte qual o novo valor de limite desejado em reais."
                    )
            else:
                st.session_state.waiting_for = "limit_value"
                response = agent.send_message(
                    "O cliente quer aumentar o limite. Pergunte qual o novo valor de limite desejado em reais."
                )
        
        elif any(word in user_lower for word in ["entrevista", "melhorar score", "score"]):
            switch_agent("entrevista")
            agent = get_current_agent()
            st.session_state.interview_step = 1
            st.session_state.waiting_for = "interview_renda"
            response = agent.send_message(
                "O cliente quer fazer entrevista de crédito. Explique que faremos algumas perguntas financeiras e comece perguntando a renda mensal em reais."
            )
        
        elif st.session_state.current_agent == "entrevista" and "interview" in st.session_state.waiting_for:
            agent = get_current_agent()
            
            if st.session_state.waiting_for == "interview_renda":
                try:
                    renda = float(user_input.replace("R$", "").replace(".", "").replace(",", ".").strip())
                    agent.set_interview_data("renda_mensal", renda)
                    st.session_state.waiting_for = "interview_emprego"
                    response = agent.send_message(
                        "Registrado. Pergunte agora o tipo de emprego: formal, autônomo ou desempregado."
                    )
                except ValueError:
                    response = agent.send_message(
                        "Valor inválido. Peça a renda mensal em reais novamente."
                    )
            
            elif st.session_state.waiting_for == "interview_emprego":
                emprego = user_input.lower().strip()
                if any(tipo in emprego for tipo in ["formal", "autônomo", "autônomo", "desempregado"]):
                    if "formal" in emprego:
                        agent.set_interview_data("tipo_emprego", "formal")
                    elif "autônomo" in emprego or "autônomo" in emprego:
                        agent.set_interview_data("tipo_emprego", "autônomo")
                    else:
                        agent.set_interview_data("tipo_emprego", "desempregado")
                    st.session_state.waiting_for = "interview_despesas"
                    response = agent.send_message(
                        "Anotado. Pergunte agora as despesas fixas mensais em reais."
                    )
                else:
                    response = agent.send_message(
                        "Tipo de emprego não reconhecido. Peça para escolher: formal, autônomo ou desempregado."
                    )
            
            elif st.session_state.waiting_for == "interview_despesas":
                try:
                    despesas = float(user_input.replace("R$", "").replace(".", "").replace(",", ".").strip())
                    agent.set_interview_data("despesas_fixas", despesas)
                    st.session_state.waiting_for = "interview_dependentes"
                    response = agent.send_message(
                        "Registrado. Pergunte quantos dependentes o cliente possui."
                    )
                except ValueError:
                    response = agent.send_message(
                        "Valor inválido. Peça as despesas fixas em reais novamente."
                    )
            
            elif st.session_state.waiting_for == "interview_dependentes":
                try:
                    dependentes = int(user_input.strip())
                    agent.set_interview_data("numero_dependentes", dependentes)
                    st.session_state.waiting_for = "interview_dividas"
                    response = agent.send_message(
                        "Anotado. Pergunte se o cliente possui dívidas ativas (sim ou não)."
                    )
                except ValueError:
                    response = agent.send_message(
                        "Valor inválido. Peça o número de dependentes novamente."
                    )
            
            elif st.session_state.waiting_for == "interview_dividas":
                dividas = user_input.lower().strip()
                if "sim" in dividas or "tenho" in dividas or "possuo" in dividas:
                    agent.set_interview_data("dividas_ativas", "sim")
                elif "não" in dividas or "nao" in dividas or "n" in dividas:
                    agent.set_interview_data("dividas_ativas", "não")
                else:
                    response = agent.send_message(
                        "Resposta não reconhecida. Pergunte novamente se possui dívidas ativas (sim ou não)."
                    )
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    return
                
                # Finalize interview
                result = agent.finalize_interview()
                if result.get("status") == "sucesso":
                    novo_score = result.get("novo_score")
                    st.session_state.authenticated_client["score_credito"] = str(novo_score)
                    st.session_state.waiting_for = None
                    st.session_state.last_agent_question = None
                    st.session_state.current_agent = "entrevista"
                    agent = get_current_agent()
                    response = agent.send_message(
                        f"Entrevista finalizada! {result.get('mensagem')}. Agradeça e pergunte se deseja solicitar aumento de limite agora ou fazer outra coisa."
                    )
                else:
                    response = agent.send_message(
                        f"Erro ao finalizar entrevista: {result.get('mensagem')}"
                    )
        
        else:
            # General conversation
            response = agent.send_message(
                f"O cliente disse: '{user_input}'. Responda de forma educada e pergunte como pode ajudar. Mencione as opções: consultar limite, aumentar limite, entrevista de crédito, consultar câmbio ou sair."
            )
    
    else:
        response = "Por favor, complete a autenticação primeiro."
    
    # Add agent response to history
    st.session_state.messages.append({"role": "assistant", "content": response})


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Banco Ágil - Atendimento ao Cliente",
        page_icon="🏦",
        layout="wide",
    )

    st.title("🏦 Banco Ágil - Atendimento ao Cliente")
    st.markdown("Converse com nossos agentes virtuais para realizar suas operações bancárias!")

    # Initialize session state
    initialize_session_state()

    # Check if API key is set
    if not os.getenv("GOOGLE_API_KEY"):
        st.error("❌ GOOGLE_API_KEY não configurada. Por favor, configure a variável de ambiente.")
        st.info("Use: `export GOOGLE_API_KEY='your-api-key'` ou configure em um arquivo .env")
        return

    # Create layout
    chat_col, sidebar_col = st.columns([3, 1])

    with chat_col:
        st.subheader("💬 Conversa")
        
        # Display chat messages
        chat_container = st.container(height=500)
        with chat_container:
            for message in st.session_state.messages:
                if message["role"] == "user":
                    st.markdown(f"**👤 Você:** {message['content']}")
                else:
                    st.markdown(f"**🤖 Agente:** {message['content']}")
        
        # Chat input
        if st.session_state.waiting_for != "finished":
            user_input = st.chat_input("Digite sua mensagem...")
            if user_input:
                process_user_message(user_input)
                st.rerun()
        else:
            st.info("✅ Atendimento encerrado. Obrigado por usar o Banco Ágil!")
            if st.button("🔄 Iniciar Novo Atendimento"):
                st.session_state.clear()
                st.rerun()

    with sidebar_col:
        st.subheader("ℹ️ Informações")
        
        # Display current agent
        agent_names = {
            "triagem": "🏦 Triagem",
            "credito": "💳 Crédito",
            "entrevista": "📋 Entrevista",
            "cambio": "💱 Câmbio"
        }
        st.markdown(f"**Agente Atual:** {agent_names.get(st.session_state.current_agent, 'Desconhecido')}")
        
        # Display client info if authenticated
        if st.session_state.authenticated_client:
            st.markdown("---")
            st.subheader("👤 Cliente")
            client = st.session_state.authenticated_client
            st.markdown(f"**Nome:** {client.get('nome')}")
            st.markdown(f"**CPF:** {client.get('cpf')[:3]}.***.***-{client.get('cpf')[-2:]}")
            st.markdown(f"**Score:** {client.get('score_credito')}")
            st.markdown(f"**Limite:** R$ {float(client.get('limite_credito', 0)):,.2f}")
            
            st.markdown("---")
            if st.button("🔐 Encerrar Sessão"):
                st.session_state.clear()
                st.rerun()
        else:
            st.info("👤 Aguardando autenticação...")
        
        st.markdown("---")
        st.markdown("### 💡 Dicas")
        st.markdown("""
        - Digite seu CPF (11 dígitos)
        - Informe sua data de nascimento
        - Converse naturalmente com o agente
        - Peça para consultar limite, aumentar limite, fazer entrevista ou consultar câmbio
        """)


if __name__ == "__main__":
    main()
