import pandas as pd
from datetime import datetime
import os

def save_to_excel(user_data, excel_path):
    try:
        if os.path.exists(excel_path):
            df = pd.read_excel(excel_path)
        else:
            df = pd.DataFrame()
        
        user_data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_row = pd.DataFrame([user_data])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_excel(excel_path, index=False)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def get_all_users(excel_path):
    try:
        if os.path.exists(excel_path):
            df = pd.read_excel(excel_path)
            return df.to_dict('records')
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []

def search_users(search_term, excel_path):
    try:
        if os.path.exists(excel_path):
            df = pd.read_excel(excel_path)
            result = df[df['name'].str.contains(search_term, case=False, na=False) | 
                       df['job_type'].str.contains(search_term, case=False, na=False)]
            return result.to_dict('records')
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []
