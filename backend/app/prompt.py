# app/prompt.py
from typing import Dict, List

class PromptBuilder:
    @staticmethod
    def build_system_prompt(rag_results: Dict[str, List[str]]) -> str:
        """
        构建 System Prompt。
        rag_results['ddl'] 里已经包含了 /* Database: xxx */ 的注释，LLM 会懂的。
        """
        ddl = "\n\n".join(rag_results.get('ddl', [])) or "No related tables found."
        docs = "\n".join([f"- {d}" for d in rag_results.get('doc', [])]) or "None"
        sqls = "\n".join([f"Example: {s}" for s in rag_results.get('sql', [])]) or "None"

        return f"""
You are an expert Data Analyst (Vanna-style).
Answer the user's question using the provided context.

### 1. Available Database Tables (DDL)
**CRITICAL:** The database name is specified in the comments (e.g., /* Database: lpcarnet */).
When writing SQL, ALWAYS use the full `database.table` syntax (e.g., `SELECT * FROM lpcarnet.car_base_info`).

{ddl}

### 2. Documentation
{docs}

### 3. Similar SQL Examples
{sqls}

### Rules
1. **SQL First:** Use `execute_sql` to get data.
2. **Explicit DB:** Always prefix tables with their database name found in the DDL.
3. **ReadOnly:** SELECT only.
4. **Visualization:** After getting data, if suitable, use `generate_chart`.
5. **Analysis:** If complex calculation is needed, use `execute_python`.
"""

    @staticmethod
    def build_analysis_prompt(data_preview: str, length: int) -> str:
        return f"""
You are a Data Analyst. Data is already loaded in memory (pandas df).
DO NOT query SQL again.
Analyze this data ({length} rows):
{data_preview}
Use `execute_python` for calculation or `generate_chart` for plotting.
"""