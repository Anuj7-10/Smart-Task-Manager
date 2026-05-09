import pandas as pd
import numpy as np

def get_task_statistics(tasks):
    # If the user has no tasks yet, return zeros so the app doesn't crash
    if not tasks:
        return {
            'total': 0, 
            'completed': 0, 
            'pending': 0, 
            'percentage': 0.0
        }

    # 1. Convert our database task objects into a format Pandas understands (a list of dictionaries)
    task_data = [{'status': task.status} for task in tasks]
    
    # 2. Create the Pandas DataFrame
    df = pd.DataFrame(task_data)
    
    # 3. Calculate the stats using Pandas
    total_tasks = len(df)
    completed_tasks = len(df[df['status'] == 'Completed'])
    pending_tasks = len(df[df['status'] == 'Pending'])
    
    # 4. Calculate the percentage using NumPy to handle the math and rounding safely
    percentage = np.round((completed_tasks / total_tasks) * 100, 1)
    
    return {
        'total': total_tasks,
        'completed': completed_tasks,
        'pending': pending_tasks,
        'percentage': percentage
    }