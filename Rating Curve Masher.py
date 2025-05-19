
"""
This script reads in two sation/elevation profiles from an excel file, interpolates them to a common station spacing, and then combines them into a single profile.
It then filters the combined profile to only include rows where the elevation changes by more than 0.02 ft from the previous row.
"""
# %%
import numpy as np
import pandas as pd

# %%
# read in each profile line from an excel file
x = r"P:\MBM\py\RAS_CamdenLakeSpillywayRatingInterpolation\SA#3 Restored Profile.xlsx"
# tthe profiles are on the sheet "Restored Spillway" and there are two:
#  Profile 1 has a header of "Shifted Restored" and Profile 2 has a header of "RAS Spillway". Each then have two columns of: "Station" and "Elevation".
seawall_profile = pd.read_excel(x, sheet_name="ShiftedForRAS", header=1, usecols="A:B", skiprows=0)
ras_profile = pd.read_excel(x, sheet_name="ShiftedForRAS", header=1, usecols="D:E", skiprows=0)
seawall_profile.columns = ["Station", "Elevation"]
ras_profile.columns = ["Station", "Elevation"]

# %%
seawall_profile
# %%
ras_profile
# %%
# get the sheet nameds from x
pd.ExcelFile(x).sheet_names

# %%
# interpolate the profiles to a common station spacing
interpolation_spacing = .5 # ft
# Create a common station range
common_min = min(seawall_profile["Station"].min(), ras_profile["Station"].min())
common_max = max(seawall_profile["Station"].max(), ras_profile["Station"].max())
# Create common station points (uniform spacing)
common_stations = np.arange(common_min, common_max, interpolation_spacing)
# Interpolate the profiles to the common station points and result in a dataframe
seawall_profile_interp = pd.DataFrame({"Station": common_stations})
ras_profile_interp = pd.DataFrame({"Station": common_stations})
seawall_profile_interp["Elevation"] = np.interp(common_stations, seawall_profile["Station"], seawall_profile["Elevation"])
ras_profile_interp["Elevation"] = np.interp(common_stations, ras_profile["Station"], ras_profile["Elevation"])

# %%
seawall_profile_interp

# %%
# take the maximum elevation of the two profiles at each station, if the station is not in both profiles, use the elevation from the profile that has it
combined_profile = pd.DataFrame({"Station": common_stations})
combined_profile["Elevation"] = np.nanmax(
    np.array([
        np.interp(common_stations, seawall_profile_interp["Station"], seawall_profile_interp["Elevation"], left=np.nan, right=np.nan),
        np.interp(common_stations, ras_profile_interp["Station"], ras_profile_interp["Elevation"], left=np.nan, right=np.nan)
    ]),
    axis=0
)
combined_profile["Elevation"] = combined_profile["Elevation"].round(2)
combined_profile
# %%
# export to csv
combined_profile.to_csv(r"P:\MBM\py\RAS_CamdenLakeSpillywayRatingInterpolation\SA#3 Restored Profile.csv", index=False)
# %%
# lets reduce the number of rows by only including changes in elevation from the previous row of more than 0.02'
# Initialize a list with the first row
filtered_rows = [combined_profile.iloc[0]]
# Iterate and keep rows where elevation change ≥ 0.02 ft
prev_elev = combined_profile.iloc[0]["Elevation"]

for idx, row in combined_profile.iterrows():
    if (abs(row["Elevation"] - prev_elev) >= 0.02) or (abs(row["Elevation"] - prev_elev) == 0.0):
        filtered_rows.append(row)
        prev_elev = row["Elevation"]

# Convert to DataFrame
filtered_df = pd.DataFrame(filtered_rows)
#sort by station
filtered_df = filtered_df.sort_values(by="Station").reset_index(drop=True)

print(f"Reduced from {len(combined_profile)} rows to {len(filtered_df)} rows.")
# %%
# if the elevation is the same as the previous row, and the next row, remove it
filtered_df = filtered_df[~((filtered_df["Elevation"].shift(1) == filtered_df["Elevation"]) & (filtered_df["Elevation"].shift(-1) == filtered_df["Elevation"]))]
print(f"Reduced from {len(combined_profile)} rows to {len(filtered_df)} rows.")
# %%
# Save or return the result
filtered_df.to_csv("elevation_filtered.csv", index=False)
# %%
