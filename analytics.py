import pandas as pd
import numpy as np

def get_task_statistics(tasks):
    
    if not tasks:
        return {
            'total': 0, 
            'completed': 0, 
            'pending': 0, 
            'percentage': 0.0
        }

    
    task_data = [{'status': task.status} for task in tasks]
    
    
    df = pd.DataFrame(task_data)
    
    
    total_tasks = len(df)
    completed_tasks = len(df[df['status'] == 'Completed'])
    pending_tasks = len(df[df['status'] == 'Pending'])
    
    
    percentage = np.round((completed_tasks / total_tasks) * 100, 1)
    
    return {
        'total': total_tasks,
        'completed': completed_tasks,
        'pending': pending_tasks,
        'percentage': percentage
    }