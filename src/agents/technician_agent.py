"""
Technician agent for handling technician-related queries.
This module provides an agent that can search technician information, planning, and daily reports.
"""
import pandas as pd
from io import StringIO
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from langchain_community.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
from langchain.embeddings import HuggingFaceEmbeddings
from config.settings import OPENAI_API_KEY, OPENAI_API_BASE, LLM_MODEL, LLM_TEMPERATURE, EMBEDDING_MODEL_NAME
import os
import json
import re
from datetime import datetime

# Set environment variables for Groq
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["OPENAI_API_BASE"] = OPENAI_API_BASE

# Initialize models
llm = ChatOpenAI(
    model=LLM_MODEL,
    temperature=LLM_TEMPERATURE,
)

embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

# Initialize Google Drive authentication
gauth = GoogleAuth()

# Set the client secrets file (should be in project root)
client_secrets_file = "client_secrets.json"
credentials_file = "credentials.json"

# Load client secrets if it exists
if os.path.exists(client_secrets_file):
    gauth.LoadClientConfigFile(client_secrets_file)

# Load or create credentials
if os.path.exists(credentials_file):
    gauth.LoadCredentialsFile(credentials_file)
else:
    # First time: need client_secrets.json to authenticate
    if not os.path.exists(client_secrets_file):
        raise FileNotFoundError(
            f"client_secrets.json not found in project root. "
            f"Please download it from Google Cloud Console and place it in the project root directory. "
            f"See SETUP_INSTRUCTIONS.md for details."
        )
    gauth.LocalWebserverAuth()
    gauth.SaveCredentialsFile(credentials_file)

if gauth.credentials is None:
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    gauth.Refresh()
else:
    gauth.Authorize()

gauth.SaveCredentialsFile(credentials_file)
drive = GoogleDrive(gauth)

# Load technician data
sheet_id = "1ersVCUKQXs5Z6on6GNc34SD5pGnKIbxVr2KAObdk42Q"

try:
    file = drive.CreateFile({'id': sheet_id})
    csv_content = file.GetContentString(mimetype='text/csv')
    df_technicien = pd.read_csv(StringIO(csv_content))
except Exception as e:
    print(f"Error loading technician data: {e}")
    df_technicien = pd.DataFrame()


# Tool 1: Technician Search
def search_technician(query):
    """Search for technician information including mail, phone, equipment"""
    def build_technician_retriever(df):
        texts = df.apply(lambda row: f"{row['nom']} {row['telephone']} {row['mail']} {row['equipement']}", axis=1).tolist()
        metadatas = df.to_dict(orient="records")
        vectorstore = FAISS.from_texts(texts, embedding_model, metadatas=metadatas)
        return vectorstore
    
    if df_technicien.empty:
        return "No technician data available."
    
    retriever = build_technician_retriever(df_technicien)
    results = retriever.similarity_search(query, k=3)
    
    search_results = [doc.page_content for doc in results]
    
    prompt = f"""Based on the following information, answer the user's question precisely and concisely.

                User Question: {query}

                Information:
                {chr(10).join([f"{i+1}. {result}" for i, result in enumerate(search_results)])}

                Answer:"""
    
    answer = llm.predict(prompt)
    return answer.strip()




# Tool 2: Planning Search for Specific Date
def search_planning_by_date(query):
    """Search planning for a specific date - handles any question type including equipment aggregation"""
    try:
        def extract_date_from_query_to_id(user_query, df_planning):
            prompt = PromptTemplate(
                input_variables=["query"],
                template="""Extract the date from the query and return it in DD-MM-YYYY format.
  - If no date is found, return NO_DATE
  - Only return the date, nothing else.

   Query: {query}"""
            )
            
            raw_response = llm.predict(prompt.format(query=user_query)).strip()
            
            if raw_response == "NO_DATE":
                return "NO_ID"
            
            matching_files = df_planning[df_planning['title'].str.contains(raw_response, case=False, na=False)]
            
            if not matching_files.empty:
                return matching_files['id'].values[0]
            else:
                return "NO_ID"
        
        def load_google_sheet(sheet_id):
            try:
                if drive.auth.credentials.access_token_expired:
                    drive.auth.LocalWebserverAuth()
                
                file = drive.CreateFile({'id': sheet_id})
                csv_content = file.GetContentString(mimetype='text/csv')
                df_plan = pd.read_csv(StringIO(csv_content))
                
                if df_plan.empty:
                    return None, None
                
                date_from_file = file['title']
                return df_plan, date_from_file
            except Exception as e:
                print(f"Error loading Google Sheet {sheet_id}: {e}")
                return None, None
        
        def aggregate_equipment(df_plan):
            """Aggregate equipment counts from all entries"""
            equipment_dict = {}
            
            for idx, row in df_plan.iterrows():
                equipment_str = str(row.get('equipment', ''))
                if pd.isna(equipment_str) or equipment_str == 'nan' or equipment_str == '':
                    continue
                
                items = equipment_str.split(',')
                for item in items:
                    item = item.strip()
                    if ':' in item:
                        parts = item.split(':')
                        equip_name = parts[0].strip()
                        try:
                            equip_count = int(parts[1].strip())
                            equipment_dict[equip_name] = equipment_dict.get(equip_name, 0) + equip_count
                        except:
                            continue
            
            return equipment_dict
        
        # Get list of planning files
        folder_id = "12V7P86iJMrceBDkU6INJ6DlpL0e9UqaM"
        query_files = f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.spreadsheet'"
        file_list = drive.ListFile({'q': query_files}).GetList()
        
        files_data = []
        for file in file_list:
            files_data.append({
                'title': file['title'],
                'id': file['id']
            })
        
        df_planning = pd.DataFrame(files_data)
        
        if df_planning.empty:
            return "No planning files found in the folder"
                sheet_id = extract_date_from_query_to_id(query, df_planning)
        
        if sheet_id == "NO_ID":
            return f"No planning found for the specified date. Available dates: {', '.join(df_planning['title'].tolist())}"
        
        df_plan, date_info = load_google_sheet(sheet_id)
        if df_plan is None:
            return "Could not load the planning sheet"
        
        query_lower = query.lower()
        is_equipment_query = any(keyword in query_lower for keyword in 
                                ['equipment', 'equipement', 'needed', 'required', 'total', 'list', 'all'])
        
        if is_equipment_query and ('list' in query_lower or 'all' in query_lower or 'total' in query_lower):
            equipment_totals = aggregate_equipment(df_plan)
            
            if not equipment_totals:
                return f"No equipment information found for {date_info}"
            
            equipment_list = "\n".join([f"• {equip}: {count}" for equip, count in sorted(equipment_totals.items())])
            
            answer_prompt = f"""Format this equipment list in a clear, professional way based on the user's question.

    User Question: {query}
    Date: {date_info}

    Equipment totals:
    {equipment_list}

    Provide a natural response with the formatted list."""
            
            answer = llm.predict(answer_prompt)
            return answer.strip()
        
        texts = []
        for idx, row in df_plan.iterrows():
            text = (
                f"Date: {date_info} | "
                f"Team/Person: {row.get('equipe', 'N/A')} | "
                f"Work Type: {row.get('travaux', 'N/A')} | "
                f"Vehicle: {row.get('voiture', 'N/A')} | "
                f"Driver: {row.get('conducetur', 'N/A')} | "
                f"Mission Expenses: {row.get('frais_mission', 'N/A')} | "
                f"Equipment: {row.get('equipment', 'N/A')}"
            )
            texts.append(text)
        
        metadatas = df_plan.to_dict(orient="records")
        for i, meta in enumerate(metadatas):
            meta['date'] = date_info
            meta['row_index'] = i
        
        vectorstore = FAISS.from_texts(texts, embedding_model, metadatas=metadatas)
        relevant_docs = vectorstore.similarity_search(query, k=min(len(texts), 10))
        
        if not relevant_docs:
            return "No relevant information found for this query."
        
        retrieved_entries = []
        for doc in relevant_docs:
            meta = doc.metadata
            entry = {
                'equipe': meta.get('equipe', 'N/A'),
                'travaux': meta.get('travaux', 'N/A'),
                'voiture': meta.get('voiture', 'N/A'),
                'conducetur': meta.get('conducetur', 'N/A'),
                'frais_mission': meta.get('frais_mission', 'N/A'),
                'equipment': meta.get('equipment', 'N/A')
            }
            retrieved_entries.append(entry)
        
        df_retrieved = pd.DataFrame(retrieved_entries)
        
        answer_prompt = f"""You are a planning assistant. Based on the retrieved planning data, answer the user's question clearly and naturally.

    User Question: {query}
    Date: {date_info}

    Retrieved Planning Data:
    {df_retrieved.to_string(index=False)}

    Instructions:
    - Answer the question directly and concisely
    - If asked about a specific person, focus only on that person's information
    - If asked about "what work" or "all activities", summarize all relevant entries
    - If asked about equipment lists, parse the equipment column and create a formatted list with totals
    - If asked about vehicles or expenses, provide those specific details
    - Use natural language and proper formatting
    - For lists, use bullet points or numbered format
    - Be specific with names, tasks, and details

    Answer:"""
        
        answer = llm.predict(answer_prompt)
        return answer.strip()
    
    except Exception as e:
        return f"Error searching planning: {str(e)}"


# Tool 3: Daily Report Search by Date
def search_daily_report_by_date(query):
    """Search daily reports (rapport journalier) for a specific date"""
    try:
        def extract_date_from_query(user_query):
            prompt = PromptTemplate(
                input_variables=["query"],
                template="""Extract the date from the query and return it in DD-MM-YYYY format.
- If no date is found, return NO_DATE
- Only return the date, nothing else.

Query: {query}"""
            )
            
            raw_response = llm.predict(prompt.format(query=user_query)).strip()
            return raw_response
        
        def load_sheet_by_date(spreadsheet_id, date_str):
            """Load a specific sheet from the spreadsheet by date"""
            try:
                if drive.auth.credentials.access_token_expired:
                    drive.auth.LocalWebserverAuth()
                
                file = drive.CreateFile({'id': spreadsheet_id})
                csv_content = file.GetContentString(mimetype='text/csv')
                df_report = pd.read_csv(StringIO(csv_content))
                
                if df_report.empty:
                    return None, None
                
                if 'date' in df_report.columns:
                    df_report['date'] = pd.to_datetime(df_report['date'], errors='coerce').dt.strftime('%Y-%m-%d')
                    
                    try:
                        query_date = datetime.strptime(date_str, '%d-%m-%Y').strftime('%Y-%m-%d')
                        df_report = df_report[df_report['date'] == query_date]
                        
                        if df_report.empty:
                            return None, date_str
                    except:
                        pass
                
                return df_report, date_str
                
            except Exception as e:
                print(f"Error loading sheet: {e}")
                return None, None
        
        def aggregate_equipment_from_reports(df_report, column='equipement_installee'):
            """Aggregate equipment from report entries"""
            equipment_dict = {}
            
            for idx, row in df_report.iterrows():
                equipment_str = str(row.get(column, ''))
                if pd.isna(equipment_str) or equipment_str == 'nan' or equipment_str == '':
                    continue
                
                items = equipment_str.split(',')
                for item in items:
                    item = item.strip()
                    if ':' in item:
                        parts = item.split(':')
                        equip_name = parts[0].strip()
                        try:
                            equip_count = int(parts[1].strip())
                            equipment_dict[equip_name] = equipment_dict.get(equip_name, 0) + equip_count
                        except:
                            continue
            
            return equipment_dict
        
        spreadsheet_id = "1c-lhkk7LPw00d5OfNiEp15CZXlVIWjUI-mI2BEYzuBs"
        
        date_str = extract_date_from_query(query)
        
        if date_str == "NO_DATE":
            return "Please specify a date for the daily report query."
        
        # Load the sheet data
        df_report, date_info = load_sheet_by_date(spreadsheet_id, date_str)
        
        if df_report is None or df_report.empty:
            return f"No daily report data found for {date_str}. Please check if the date is correct."
        
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in ['equipment', 'equipement', 'installed', 'installée', 'total']):
            if 'list' in query_lower or 'all' in query_lower or 'total' in query_lower:
                equipment_totals = aggregate_equipment_from_reports(df_report, 'equipement_installee')
                
                if not equipment_totals:
                    return f"No equipment installation information found for {date_info}"
                
                equipment_list = "\n".join([f"• {equip}: {count}" for equip, count in sorted(equipment_totals.items())])
                
                answer_prompt = f"""Format this equipment installation list based on the user's question.

User Question: {query}
Date: {date_info}

Equipment installed:
{equipment_list}

Provide a natural response with the formatted list."""
                
                answer = llm.predict(answer_prompt)
                return answer.strip()
        
        # Handle equipment return queries
        if 'retour' in query_lower or 'return' in query_lower:
            equipment_returns = aggregate_equipment_from_reports(df_report, 'equipement_retour')
            
            if not equipment_returns:
                return f"No equipment return information found for {date_info}"
            
            equipment_list = "\n".join([f"• {equip}: {count}" for equip, count in sorted(equipment_returns.items())])
            
            answer_prompt = f"""Format this equipment return list based on the user's question.

User Question: {query}
Date: {date_info}

Equipment returned:
{equipment_list}

Provide a natural response with the formatted list."""
            
            answer = llm.predict(answer_prompt)
            return answer.strip()
        
        texts = []
        for idx, row in df_report.iterrows():
            text = (
                f"Date: {date_info} | "
                f"Client: {row.get('client', 'N/A')} | "
                f"Delivery Note: {row.get('nom_BL', 'N/A')} | "
                f"Site Manager: {row.get('chef_chantier', 'N/A')} | "
                f"Entry Time: {row.get('heure_entree', 'N/A')} | "
                f"Exit Time: {row.get('heure_sortie', 'N/A')} | "
                f"Planned Action: {row.get('action_previsionelle_a_executer', 'N/A')} | "
                f"Equipment Installed: {row.get('equipement_installee', 'N/A')} | "
                f"Constraints: {row.get('contrainte_visees', 'N/A')} | "
                f"Remaining Work: {row.get('reste_a_faire', 'N/A')} | "
                f"Observations: {row.get('observation', 'N/A')} | "
                f"Needs for Tomorrow: {row.get('besoin_ressentis_pour_demain', 'N/A')} | "
                f"Equipment Returned: {row.get('equipement_retour', 'N/A')}"
            )
            texts.append(text)
        
        metadatas = df_report.to_dict(orient="records")
        for i, meta in enumerate(metadatas):
            meta['date'] = date_info
            meta['row_index'] = i
        
        vectorstore = FAISS.from_texts(texts, embedding_model, metadatas=metadatas)
        relevant_docs = vectorstore.similarity_search(query, k=min(len(texts), 10))
        
        if not relevant_docs:
            return "No relevant information found for this query."
        
        # Build retrieved entries
        retrieved_entries = []
        for doc in relevant_docs:
            meta = doc.metadata
            entry = {
                'client': meta.get('client', 'N/A'),
                'nom_BL': meta.get('nom_BL', 'N/A'),
                'chef_chantier': meta.get('chef_chantier', 'N/A'),
                'heure_entree': meta.get('heure_entree', 'N/A'),
                'heure_sortie': meta.get('heure_sortie', 'N/A'),
                'action_previsionelle_a_executer': meta.get('action_previsionelle_a_executer', 'N/A'),
                'equipement_installee': meta.get('equipement_installee', 'N/A'),
                'contrainte_visees': meta.get('contrainte_visees', 'N/A'),
                'reste_a_faire': meta.get('reste_a_faire', 'N/A'),
                'observation': meta.get('observation', 'N/A'),
                'besoin_ressentis_pour_demain': meta.get('besoin_ressentis_pour_demain', 'N/A'),
                'equipement_retour': meta.get('equipement_retour', 'N/A')
            }
            retrieved_entries.append(entry)
        
        df_retrieved = pd.DataFrame(retrieved_entries)
        
        answer_prompt = f"""You are a daily report assistant. Based on the retrieved daily report data, answer the user's question clearly and naturally.

User Question: {query}
Date: {date_info}

Retrieved Daily Report Data:
{df_retrieved.to_string(index=False)}

Instructions:
- Answer the question directly and concisely
- If asked about a specific client, focus only on that client's work
- If asked about work done, summarize the actions executed
- If asked about constraints or problems, highlight those issues
- If asked about remaining work, list what's left to do
- If asked about time spent, calculate from entry/exit times
- If asked about observations or needs, provide those details
- Use natural language and proper formatting
- For calculations (time, totals), perform them accurately
- Be specific with client names, actions, and equipment

Answer:"""
        
        answer = llm.predict(answer_prompt)
        return answer.strip()
    
    except Exception as e:
        return f"Error searching daily reports: {str(e)}"


# Tool 4: Advanced Merged Daily Reports Search
def search_merged_data(query):
    """Search across all daily report data for complex queries spanning multiple dates"""
    try:
        def load_all_daily_reports():
            """Load all daily report data from multiple files in the folder"""
            try:
                if drive.auth.credentials.access_token_expired:
                    drive.auth.LocalWebserverAuth()
                
                # Folder containing all daily reports
                folder_id = "1t8RpUifcNYA66105dQ2QVLbNH8WAR94O"
                query_files = f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.spreadsheet'"
                file_list = drive.ListFile({'q': query_files}).GetList()
                
                print(f"Found {len(file_list)} files in folder")
                
                all_reports = []
                
                for file in file_list:
                    try:
                        print(f"Loading: {file['title']}")
                        sheet = drive.CreateFile({'id': file['id']})
                        csv_content = sheet.GetContentString(mimetype='text/csv')
                        df = pd.read_csv(StringIO(csv_content))
                        
                        if not df.empty:
                            if 'date' in df.columns:
                                df['date_parsed'] = pd.to_datetime(df['date'], errors='coerce')
                            else:
                                date_match = re.search(r'(\d{2}-\d{2}-\d{4})', file['title'])
                                if date_match:
                                    date_str = date_match.group(1)
                                    df['date'] = date_str
                                    df['date_parsed'] = pd.to_datetime(date_str, format='%d-%m-%Y', errors='coerce')
                            
                            all_reports.append(df)
                            print(f"✓ Loaded {len(df)} entries from {file['title']}")
                    except Exception as e:
                        print(f"✗ Error loading file {file['title']}: {e}")
                        continue
                
                if all_reports:
                    df_combined = pd.concat(all_reports, ignore_index=True)
                    print(f"\n✓ Total: {len(df_combined)} entries from {len(all_reports)} files")
                    return df_combined
                
                return pd.DataFrame()
                
            except Exception as e:
                print(f"Error loading daily reports folder: {e}")
                import traceback
                traceback.print_exc()
                return pd.DataFrame()
        
        def extract_filters_from_query(user_query):
            """Use LLM to extract filtering criteria from query"""
            filter_prompt = f"""Analyze this query and extract filtering information. Return a JSON object.

Query: {user_query}

Extract these fields (use null if not mentioned):
- date_range: {{"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}} or null
- month: month name or number (e.g., "july" or "7" or "august" or "8") or null  
- year: year (e.g., "2025") or null
- client: specific client name or null
- site_manager: chef_chantier name or null
- equipment_type: specific equipment type ONLY if user asks about PARTICULAR equipment (e.g., "camera", "alarme") or null
- work_type: type of work/action or null
- constraint: mentioned constraints or problems or null
- aggregation: "list" if user asks "what", "show", "list" or "total" if user asks for counts/totals or null
- delivery_note: BL number or null

IMPORTANT: 
- If user asks "what equipment" without specifying type, set equipment_type to null and aggregation to "list"
- Don't filter by the word "equipment" itself
- Recognize month names in different languages (july/juillet, august/août)

Return ONLY valid JSON, nothing else."""
            
            try:
                filter_response = llm.predict(filter_prompt).strip()
                # Clean up response
                if '```json' in filter_response:
                    filter_response = filter_response.split('```json')[1].split('```')[0].strip()
                elif '```' in filter_response:
                    filter_response = filter_response.split('```')[1].split('```')[0].strip()
                
                filters = json.loads(filter_response)
                return filters
            except Exception as e:
                print(f"Error extracting filters: {e}")
                return {}
        
        def apply_filters(df, filters):
            """Apply filters to dataframe"""
            filtered_df = df.copy()
            
            print(f"Starting with {len(filtered_df)} rows")
            
            # Date filtering
            if 'date_parsed' in filtered_df.columns:
                # Month filter
                if filters.get('month'):
                    month = str(filters['month']).lower()
                    month_map = {
                        'january': 1, 'janvier': 1, 'février': 2, 'february': 2, 
                        'march': 3, 'mars': 3, 'april': 4, 'avril': 4,
                        'may': 5, 'mai': 5, 'june': 6, 'juin': 6, 
                        'july': 7, 'juillet': 7, 'august': 8, 'août': 8,
                        'september': 9, 'septembre': 9, 'october': 10, 'octobre': 10, 
                        'november': 11, 'novembre': 11, 'december': 12, 'décembre': 12,
                        '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
                        '7': 7, '8': 8, '9': 9, '10': 10, '11': 11, '12': 12
                    }
                    
                    if month in month_map:
                        month_num = month_map[month]
                        filtered_df = filtered_df[filtered_df['date_parsed'].dt.month == month_num]
                        print(f"After month filter ({month} = {month_num}): {len(filtered_df)} rows")
                
                # Year filter
                if filters.get('year'):
                    try:
                        year = int(filters['year'])
                        filtered_df = filtered_df[filtered_df['date_parsed'].dt.year == year]
                        print(f"After year filter ({year}): {len(filtered_df)} rows")
                    except:
                        pass
                
                # Date range filter
                if filters.get('date_range'):
                    try:
                        start = pd.to_datetime(filters['date_range'].get('start'))
                        end = pd.to_datetime(filters['date_range'].get('end'))
                        filtered_df = filtered_df[
                            (filtered_df['date_parsed'] >= start) & 
                            (filtered_df['date_parsed'] <= end)
                        ]
                        print(f"After date range filter: {len(filtered_df)} rows")
                    except:
                        pass
            
            # Client filter
            if filters.get('client') and 'client' in filtered_df.columns:
                client = str(filters['client']).lower()
                filtered_df = filtered_df[
                    filtered_df['client'].str.lower().str.contains(client, na=False, regex=False)
                ]
                print(f"After client filter ({client}): {len(filtered_df)} rows")
            
            # Site manager filter
            if filters.get('site_manager') and 'chef_chantier' in filtered_df.columns:
                manager = str(filters['site_manager']).lower()
                filtered_df = filtered_df[
                    filtered_df['chef_chantier'].str.lower().str.contains(manager, na=False, regex=False)
                ]
                print(f"After manager filter: {len(filtered_df)} rows")
            
            # Equipment TYPE filter (only if specific equipment mentioned)
            if filters.get('equipment_type'):
                equipment = str(filters['equipment_type']).lower()
                equipment_columns = ['equipement_installee', 'equipement_retour']
                
                mask = pd.Series([False] * len(filtered_df))
                for col in equipment_columns:
                    if col in filtered_df.columns:
                        mask |= filtered_df[col].str.lower().str.contains(equipment, na=False, regex=False)
                
                filtered_df = filtered_df[mask]
                print(f"After equipment type filter ({equipment}): {len(filtered_df)} rows")
            
            return filtered_df
        
        def aggregate_equipment(df, column='equipement_installee'):
            """Aggregate equipment from multiple rows"""
            equipment_dict = {}
            
            if column not in df.columns:
                return equipment_dict
            
            for idx, row in df.iterrows():
                equipment_str = str(row.get(column, ''))
                if pd.isna(equipment_str) or equipment_str == 'nan' or equipment_str == '':
                    continue
                
                items = equipment_str.split(',')
                for item in items:
                    item = item.strip()
                    if ':' in item:
                        parts = item.split(':')
                        equip_name = parts[0].strip()
                        try:
                            equip_count = int(parts[1].strip())
                            equipment_dict[equip_name] = equipment_dict.get(equip_name, 0) + equip_count
                        except:
                            continue
            
            return equipment_dict
        
        filters = extract_filters_from_query(query)
        print(f"Extracted filters: {filters}")
        
        print("\nLoading all daily reports...")
        df_reports = load_all_daily_reports()
        
        if df_reports.empty:
            return "No daily report data available."
        
        print(f"\nLoaded {len(df_reports)} total report entries")
        
        # Apply filters
        df_filtered = apply_filters(df_reports, filters)
        
        if df_filtered.empty:
            return f"No data found matching the criteria. Filters applied: {filters}\nPlease check if the date/month/client exists in the data."
        
        print(f"\nFiltered to {len(df_filtered)} rows")
        
        query_lower = query.lower()
        
        # Handle equipment aggregation queries
        if filters.get('aggregation') in ['list', 'total', 'count', 'sum']:
            
            # Equipment installed
            if any(keyword in query_lower for keyword in ['equipment', 'equipement']):
                equipment_installed = aggregate_equipment(df_filtered, 'equipement_installee')
                equipment_returned = aggregate_equipment(df_filtered, 'equipement_retour')
                
                show_installed = 'installed' in query_lower or 'installée' in query_lower or 'utilisé' in query_lower or 'used' in query_lower or ('equipment' in query_lower and 'return' not in query_lower)
                show_returned = 'return' in query_lower or 'retour' in query_lower
                
                if not show_installed and not show_returned:
                    show_installed = True
                
                result_text = ""
                
                if show_installed and equipment_installed:
                    equipment_list = "\n".join([f"• {equip}: {count}" for equip, count in sorted(equipment_installed.items(), key=lambda x: x[1], reverse=True)])
                    result_text += f"Equipment Installed:\n{equipment_list}\n\n"
                
                if show_returned and equipment_returned:
                    equipment_list = "\n".join([f"• {equip}: {count}" for equip, count in sorted(equipment_returned.items(), key=lambda x: x[1], reverse=True)])
                    result_text += f"Equipment Returned:\n{equipment_list}\n"
                
                if not result_text:
                    return "No equipment information found for the specified criteria."
                
                answer_prompt = f"""Format this equipment data based on the user's question.

User Question: {query}
Filters Applied: {filters}
Total Records: {len(df_filtered)}

{result_text}

Provide a clear, natural response with summary."""
                
                answer = llm.predict(answer_prompt)
                return answer.strip()
        
        # For non-aggregation queries, use vector retrieval
        df_sample = df_filtered.head(100) if len(df_filtered) > 100 else df_filtered
        
        # Build rich text representations
        texts = []
        for idx, row in df_sample.iterrows():
            text = (
                f"Date: {row.get('date', 'N/A')} | "
                f"Client: {row.get('client', 'N/A')} | "
                f"BL: {row.get('nom_BL', 'N/A')} | "
                f"Manager: {row.get('chef_chantier', 'N/A')} | "
                f"Time: {row.get('heure_entree', 'N/A')}-{row.get('heure_sortie', 'N/A')} | "
                f"Action: {row.get('action_previsionelle_a_executer', 'N/A')} | "
                f"Equipment Installed: {row.get('equipement_installee', 'N/A')} | "
                f"Constraints: {row.get('contrainte_visees', 'N/A')} | "
                f"Remaining: {row.get('reste_a_faire', 'N/A')} | "
                f"Observations: {row.get('observation', 'N/A')}"
            )
            texts.append(text)
        
        metadatas = df_sample.to_dict(orient="records")
        
        # Create vectorstore
        vectorstore = FAISS.from_texts(texts, embedding_model, metadatas=metadatas)
        relevant_docs = vectorstore.similarity_search(query, k=min(20, len(texts)))
        
        if not relevant_docs:
            return "No relevant information found."
        
        # Format results
        results_data = [doc.metadata for doc in relevant_docs]
        df_results = pd.DataFrame(results_data)
        
        # Use LLM to generate final answer
        answer_prompt = f"""You are a daily report analyst. Answer the user's question based on the data.

User Question: {query}
Total matching records: {len(df_filtered)}
Sample size: {len(df_results)}

Data:
{df_results.to_string(index=False, max_rows=25)}

Provide a comprehensive, clear answer with specific details."""
        
        answer = llm.predict(answer_prompt)
        return answer.strip()
        
    except Exception as e:
        import traceback
        return f"Error in merged data search: {str(e)}\n{traceback.format_exc()}"


# Create tools
tools = [
    Tool(
        name="technician_search",
        description="Use this tool when user asks about technician information like mail, phone, or equipment",
        func=search_technician,
        return_direct=True
    ),
    Tool(
        name="daily_report_search",
        description="""Use this tool when user asks about DAILY REPORTS (rapport journalier) for a specific date, including:
        - What was done for a specific client
        - Work completed on a date
        - Equipment installed on a date
        - Constraints or problems encountered
        - Remaining work (reste à faire)
        - Observations or needs for tomorrow
        - Time spent on site (entry/exit times)
        - Equipment returned""",
        func=search_daily_report_by_date,
        return_direct=True
    ),
    Tool(
        name="planning_date_search", 
        description="""Use this tool when user asks ANY question about planning for a SPECIFIC DATE, including:
        - What a specific person is doing on a date
        - All work/activities happening on a date
        - What equipment is being used on a date
        - Which vehicles are in use on a date
        - Mission expenses for a date
        - Any other date-specific planning question""",
        func=search_planning_by_date,
        return_direct=True
    ),
    Tool(
        name="merged_data_search",
        description="""Use this tool when user asks complex questions about daily reports across MULTIPLE dates, time periods, or all data, including:
        - Work done for a client across multiple dates
        - Equipment used in a specific month or period
        - All work done by a site manager over time
        - Problems/constraints encountered during a period
        - Total hours worked in a month
        - Any analysis requiring data from multiple dates""",
        func=search_merged_data,
        return_direct=True
    )
]


# Initialize agent
def create_agent():
    """Create and return the LangChain agent"""
    return initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        max_iterations=10,
        early_stopping_method="generate",
        handle_parsing_errors=True
    )


# Main function to run the agent
def run_agent(user_question: str) -> str:
    """
    Run the technician agent to answer a question.
    
    Args:
        user_question: User question about technicians, planning, or daily reports
    
    Returns:
        Agent response as string
    """
    try:
        agent = create_agent()
        response = agent.run(user_question)
        return response
    except Exception as e:
        return f"Error calling agent: {str(e)}"
