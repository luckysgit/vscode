import pandas as pd

url = "https://en.wikipedia.org/wiki/List_of_The_Simpsons_episodes_(seasons_1%E2%80%9320)"
simpson = pd.read_html(url)

print(len(simpson))   # number of tables found
print(simpson[0].head())  # show first table

