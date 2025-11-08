"""
UI components for different sections of the application.
"""
import streamlit as st
import pandas as pd
from src.agents.technician_agent import run_agent
from src.retrievers.qa_chains import ask_product_question, ask_product_question_satel
from src.retrievers.product_analysis import search_selected_products_tool_dual_df, search_selected_products_tool_dual_df_satel
from src.utils.session_state import add_custom_product, remove_custom_product, reset_search, initialize_session_state
from src.utils.search import search_products_with_code


def render_technician_interface():
    """Render the technician query interface."""
    st.markdown('<div class="section-title">Technicien Queries</div>', unsafe_allow_html=True)
    
    # Display chat history
    if st.session_state.technicien_chat_history:
        st.markdown("### 💬 Conversation History")
        
        for i, chat in enumerate(st.session_state.technicien_chat_history):
            # User question
            st.markdown(f"""
            <div style="background-color: #e3f2fd; padding: 12px; border-radius: 8px; margin: 8px 0;">
                <strong>🧑 You:</strong> {chat['question']}
            </div>
            """, unsafe_allow_html=True)
            
            # Agent answer
            st.markdown(f"""
            <div style="background-color: #f5f5f5; padding: 12px; border-radius: 8px; margin: 8px 0;">
                <strong>🤖 Agent:</strong> {chat['answer']}
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
    
    # Input section
    st.markdown("### ✍️ Ask about Technicians")
    
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_question = st.text_input(
            "Your question:",
            placeholder="e.g., What is John's phone number?",
            key="tech_input"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        ask_button = st.button("🚀 Ask", use_container_width=True)
    
    # Clear chat button
    if st.session_state.technicien_chat_history:
        if st.button("🗑️ Clear Chat"):
            st.session_state.technicien_chat_history = []
            st.rerun()
    
    # Process question
    if ask_button and user_question.strip():
        with st.spinner("🤔 Agent is working..."):
            try:
                # Run agent
                answer = run_agent(user_question)
                
                # Add to history
                st.session_state.technicien_chat_history.append({
                    'question': user_question,
                    'answer': answer
                })
                
                # Rerun to show updated chat
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")


def render_product_chat(product_code: str, category: str, llm, specs_index: dict, specs_index_pdf: dict, embedding_model):
    """Render product chat interface."""
    st.markdown(f"### Chat about product: {product_code}")

    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = {}
    if product_code not in st.session_state['chat_history']:
        st.session_state['chat_history'][product_code] = []

    # Display history (above input)
    for chat in st.session_state['chat_history'][product_code]:
        with st.chat_message("user", avatar="👤"):
            st.markdown(chat["question"])
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(chat["answer"])
            if chat["sources"]:
                with st.expander("Sources"):
                    for s in chat["sources"]:
                        st.markdown(f"- {s}...")

    # User input (chat style)
    if prompt := st.chat_input(f"Ask your question about {product_code}:"):
        # Show user message immediately
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # Get LLM answer
        if category == "Hikvision Product":
            answer = ask_product_question(product_code, prompt, llm, specs_index, specs_index_pdf, embedding_model)
        else:  # Satel Product
            answer = ask_product_question_satel(product_code, prompt, llm, specs_index, specs_index_pdf, embedding_model)

        # Show assistant message
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(answer["result"])
            if answer["source_documents"]:
                with st.expander("Sources"):
                    for doc in answer["source_documents"]:
                        st.markdown(f"- {doc.page_content[:200]}...")

        # Save to history
        st.session_state['chat_history'][product_code].append({
            "question": prompt,
            "answer": answer['result'],
            "sources": [doc.page_content[:200] for doc in answer["source_documents"]]
        })


def render_product_search_interface(category: str, df: pd.DataFrame, llm, specs_index: dict, specs_index_pdf: dict, embedding_model):
    """Render product search and analysis interface."""
    # Initialize session state
    initialize_session_state()
    
    # Section: Search Configuration
    st.markdown("### 🔍 Search Configuration")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        user_query = st.text_input(
            "Enter the type of element:", 
            placeholder="e.g., camera, recorder, switch..."
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Reset Search", help="Clear all search results and start over"):
            reset_search()
            st.rerun()

    # Section: Custom Product Management
    with st.expander("➕ Manage Custom Product Codes", expanded=False):
        st.markdown("**Add individual product codes manually:**")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            new_code = st.text_input(
                "Enter product code:", 
                key="new_product_code",
                placeholder="e.g., DS-2CD2347G2-L"
            )
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("➕ Add"):
                if new_code:
                    add_custom_product(new_code)
                    st.rerun()
        
        # Display existing custom products
        if st.session_state["custom_products"]:
            st.markdown("**Current custom products:**")
            for idx, product in enumerate(st.session_state["custom_products"]):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"• {product}")
                with col2:
                    if st.button("🗑️", key=f"remove_{idx}", help=f"Remove {product}"):
                        remove_custom_product(product)
                        st.rerun()

    # Step 1: Initial Search
    if user_query and not st.session_state["search_done"]:
        with st.spinner(f"Searching for '{user_query}'..."):
            results = search_products_with_code(df, user_query)
            st.session_state["search_done"] = True
            
            if not results.empty:
                st.markdown(f"### ✅ Found {len(results)} results for '{user_query}':")
                st.dataframe(results[['product_code', 'product_name']], use_container_width=True)
                
                # Store initial analysis in history
                st.session_state["history"].append({
                    "query": user_query,
                    "analyzed_products": results['product_code'].tolist(),
                    "results": results,
                    "type": "search"
                })
            else:
                st.warning(f"❌ No results found for: '{user_query}'")

    # Section: Analysis History and Product Selection
    if st.session_state["history"] or st.session_state["custom_products"]:
        st.markdown("### 📊 Product Analysis & Selection")
        
        # Display previous analyses
        if st.session_state["history"]:
            st.markdown("#### 🕒 Previous Search Results")
            
            for i, entry in enumerate(st.session_state["history"]):
                with st.expander(f"📋 Analysis {i+1}: '{entry['query']}'", expanded=i==len(st.session_state["history"])-1):
                    
                    # Display results table
                    st.dataframe(entry["results"], use_container_width=True)
                    
                    # Product selection with Select All functionality
                    all_products = entry["analyzed_products"]
                    
                    # Select All checkbox
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        select_all = st.checkbox(
                            "Select All", 
                            key=f"select_all_{i}",
                            help="Select/deselect all products from this analysis"
                        )
                    
                    # Main product selection from search results
                    with col2:
                        if select_all:
                            selected = st.multiselect(
                                "Selected products from search results:",
                                all_products,
                                default=all_products,
                                key=f"select_{i}"
                            )
                        else:
                            selected = st.multiselect(
                                "Select products for follow-up analysis:",
                                all_products,
                                key=f"select_{i}"
                            )
                    
                    # Manual product code addition section
                    st.markdown("**➕ Add Additional Product Codes:**")
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        additional_code = st.text_input(
                            "Enter additional product code:",
                            key=f"additional_code_{i}",
                            placeholder="e.g., DS-2CD2347G2-L, iDS-7208HQHI-M1/S..."
                        )
                    
                    with col2:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("➕ Add", key=f"add_code_{i}"):
                            if additional_code.strip():
                                code = additional_code.strip()
                                if code not in selected:
                                    selected.append(code)
                                    st.success(f"Added: {code}")
                                    st.rerun()
                                else:
                                    st.warning("Code already selected!")
                            else:
                                st.error("Please enter a product code!")
                    
                    with col3:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("🔄 Clear All", key=f"clear_all_{i}"):
                            st.rerun()
                    
                    # Add option to include global custom products
                    if st.session_state["custom_products"]:
                        include_custom = st.multiselect(
                            "➕ Include from global custom products:",
                            st.session_state["custom_products"],
                            key=f"custom_select_{i}",
                            help="Select from your saved custom product codes"
                        )
                        selected.extend(include_custom)
                    
                    # Display current selection summary
                    if selected:
                        st.markdown("**📋 Current Selection:**")
                        selection_cols = st.columns(min(4, len(selected)))
                        
                        for idx, product in enumerate(selected):
                            with selection_cols[idx % len(selection_cols)]:
                                if product in all_products:
                                    st.success(f"🔍 {product}")
                                elif product in st.session_state.get("custom_products", []):
                                    st.info(f"🏷️ {product}")
                                else:
                                    st.warning(f"➕ {product}")
                        
                        # Legend
                        st.markdown("""
                        <small>
                        🔍 = From search results | 🏷️ = From global custom | ➕ = Manually added
                        </small>
                        """, unsafe_allow_html=True)
                    
                    # Individual product code management
                    if selected:
                        st.markdown("**Selected Products with Code Options:**")
                        product_codes = {}
                        
                        cols = st.columns(min(3, len(selected)))
                        for idx, product in enumerate(selected):
                            with cols[idx % len(cols)]:
                                st.write(f"**{product}**")
                                code_option = st.radio(
                                    "Include code?",
                                    ["Oui", "Non"],
                                    key=f"code_{i}_{product}",
                                    horizontal=True
                                )
                                product_codes[product] = code_option == "Oui"
                        
                        # Follow-up query
                        followup_query = st.text_input(
                            "🔍 Enter your follow-up question about selected products:",
                            key=f"query_{i}",
                            placeholder="e.g., Compare resolution, power consumption, features..."
                        )
                        
                        if followup_query and st.button(f"🚀 Analyze Selected Products", key=f"analyze_{i}"):
                            with st.spinner("Performing detailed analysis..."):
                                # Perform follow-up analysis
                                if category == "Hikvision Product":
                                    df_followup = search_selected_products_tool_dual_df(followup_query, selected, llm, specs_index, specs_index_pdf)
                                else:  # Satel Product
                                    df_followup = search_selected_products_tool_dual_df_satel(followup_query, selected, llm, specs_index, specs_index_pdf)
                                
                                st.markdown(f"### 🔍 Follow-up Analysis: '{followup_query}'")
                                
                                # Display results
                                st.dataframe(df_followup, use_container_width=True)
                                
                                # Save results to history
                                st.session_state["history"].append({
                                    "query": followup_query,
                                    "analyzed_products": selected,
                                    "results": df_followup,
                                    "type": "followup",
                                    "code_configuration": product_codes
                                })
                                
                                st.success("✅ Analysis completed and saved to history!")
                                st.rerun()

        # Direct custom product analysis
        if st.session_state["custom_products"]:
            st.markdown("#### ➕ Direct Custom Product Analysis")
            
            with st.expander("🔧 Analyze Custom Products", expanded=False):
                custom_selected = st.multiselect(
                    "Select custom products to analyze:",
                    st.session_state["custom_products"],
                    key="direct_custom_select"
                )
                
                if custom_selected:
                    # Individual code options for custom products
                    st.markdown("**Custom Products with Code Options:**")
                    custom_codes = {}
                    
                    for product in custom_selected:
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"• {product}")
                        with col2:
                            code_option = st.radio(
                                "Code?",
                                ["Oui", "Non"],
                                key=f"custom_code_{product}",
                                horizontal=True
                            )
                            custom_codes[product] = code_option == "Oui"
                    
                    custom_query = st.text_input(
                        "Enter analysis question for custom products:",
                        key="custom_query",
                        placeholder="Analyze these specific products..."
                    )
                    
                    if custom_query and st.button("🚀 Analyze Custom Products"):
                        with st.spinner("Analyzing custom products..."):
                            if category == "Hikvision Product":
                                df_custom = search_selected_products_tool_dual_df(custom_query, custom_selected, llm, specs_index, specs_index_pdf)
                            else:  # Satel Product
                                df_custom = search_selected_products_tool_dual_df_satel(custom_query, custom_selected, llm, specs_index, specs_index_pdf)
                            
                            st.markdown(f"### 🔍 Custom Product Analysis: '{custom_query}'")
                            st.dataframe(df_custom, use_container_width=True)
                            
                            # Save to history
                            st.session_state["history"].append({
                                "query": custom_query,
                                "analyzed_products": custom_selected,
                                "results": df_custom,
                                "type": "custom",
                                "code_configuration": custom_codes
                            })
                            
                            st.success("✅ Custom analysis completed!")
                            st.rerun()

