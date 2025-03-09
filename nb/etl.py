import re 
import pandas as pd 

# Const 
INPUT_PATH = "../outputs/all_listings.pkl"

# Transform
df = pd.read_pickle(INPUT_PATH)
df["rent_FLOAT"] = df["rent"].map(lambda val : float(re.search(r"[\d,.]*", val)[0].replace(",", "")))
df["size_INT"] = df["size"].map(lambda val : int(val.replace(" m2", "")) if val else None)
df["city"] = df["location"].map(
    lambda val : re.search(r',\s*(.*)', val).group(1) if re.search(r',\s*(.*)', val) else None)

# Get 