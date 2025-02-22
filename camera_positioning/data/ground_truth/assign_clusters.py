import json
import pandas as pd
from datetime import datetime

def assign_clusters(json_path, output_path, time_threshold=5):
    """
    Reads a JSON file, groups images based on timestamp and ImageNumber order,
    and saves the updated JSON.
    
    Parameters:
        json_path (str): Path to the input JSON file.
        output_path (str): Path to save the updated JSON file.
        time_threshold (int): Time difference in seconds to define a new cluster.
    """
    # Load the JSON file
    with open(json_path, "r") as file:
        data = json.load(file)
    
    cluster_counter = 0  # Ensure the cluster numbering does not restart
    
    for sequence_name in data.keys():
        images = data[sequence_name]["items"]
        
        # Convert timestamps to datetime objects and store in a dataframe
        df = pd.DataFrame(images)
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], format="%Y:%m:%d %H:%M:%S")
        
        # Sort by ImageNumber and Timestamp to ensure chronological order
        df = df.sort_values(by=["ImageNumber", "Timestamp"]).reset_index(drop=True)
        
        # Initialize clustering
        cluster_counter += 1  # Start with a new cluster
        df.loc[0, "Cluster"] = f"Cluster{cluster_counter:02d}"
        
        # Assign clusters based on time difference and ImageNumber order
        for i in range(1, len(df)):
            time_diff = (df.loc[i, "Timestamp"] - df.loc[i - 1, "Timestamp"]).total_seconds()
            image_gap = df.loc[i, "ImageNumber"] - df.loc[i - 1, "ImageNumber"]
            
            if time_diff > time_threshold or image_gap > 1:
                cluster_counter += 1  # Increment only when necessary
            
            df.loc[i, "Cluster"] = f"Cluster{cluster_counter:02d}"
        
        # Ensure clusters are unique by printing debug information
        print(df[["ImageNumber", "Timestamp", "Cluster"]].tail(20))
        
        # Update the original JSON structure
        for i, row in df.iterrows():
            data[sequence_name]["items"][i]["Cluster"] = row["Cluster"]
    
    # Save the updated JSON to a new file
    with open(output_path, "w") as file:
        json.dump(data, file, indent=4)
    
    print(f"Updated JSON file saved to: {output_path}")

# Example usage
assign_clusters("d:/Pix4d-carroponten/camera_positioning/data/ground_truth/all_sequences.json", 
                "d:/Pix4d-carroponten/camera_positioning/data/ground_truth/all_sequences_clustered.json")
