import streamlit as st
import uproot
import matplotlib.pyplot as plt
import pandas as pd
import os

# Specify the predetermined folder
root_folder = "./uploaded_files/"

# Ensure the folder exists
if not os.path.exists(root_folder):
    os.makedirs(root_folder)

# Sidebar for file selection or upload
st.sidebar.title("ROOT File Browser")

# List ROOT files in the predetermined folder
local_files = [f for f in os.listdir(root_folder) if f.endswith(".root")]
selected_file = st.sidebar.selectbox("Select a ROOT file", ["Select a file"] + local_files)

# Upload new file if needed
uploaded_file = st.sidebar.file_uploader("Or upload a ROOT file", type=["root"])

# Determine which file to load: either from the folder or an uploaded file
file_path = None
if selected_file != "Select a file":
    file_path = os.path.join(root_folder, selected_file)
    print(file_path)
elif uploaded_file:
    file_path = uploaded_file

def build_tree(directory, path=""):
    """
    Recursively builds a nested tree structure using Streamlit's expandable elements.
    Each TTree or branch can be expanded to reveal its sub-branches or leaf nodes.
    """
    for key, obj in directory.items():
        print(key)
        full_path = f"{path}{key}"
        if isinstance(obj, uproot.behaviors.TTree.TTree):
            with st.expander(f"📂 {key}", expanded=False):
                branches = obj.keys()
                for branch in branches:
                    branch_path = f"{full_path}/{branch}"
                    if st.button(f"📈 {branch}", key=branch_path):
                        plot_branch_histogram(obj, branch)
        elif isinstance(obj, uproot.reading.ReadOnlyDirectory):
            with st.expander(f"📁 {key}", expanded=False):
                build_tree(obj, path=f"{full_path}/")

# Function to plot histogram of a selected branch
def plot_branch_histogram(tree, branch):
    """
    Plots the histogram of a selected branch from the ROOT TTree.
    """
    data = tree[branch].array(library="np")
    fig, ax = plt.subplots()
    ax.hist(data, bins=30, alpha=0.7, color="skyblue")
    ax.set_title(f"Histogram of {branch}")
    ax.set_xlabel("Value")
    ax.set_ylabel("Frequency")
    st.pyplot(fig)

if file_path:
    # Load the ROOT file using uproot
    file = uproot.open(file_path)
    st.write("### ROOT File Structure")
    # Recursively display the file structure
    build_tree(file)
else:
    st.write("Upload a ROOT file to start exploring.")
