import streamlit as st
from streamlit_tree_select import tree_select
import uproot
import matplotlib.pyplot as plt
import numpy as np
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
elif uploaded_file:
    file_path = uploaded_file

# Function to build the tree nodes
def build_tree_nodes(directory, path=""):
    nodes = []
    for key, obj in directory.items():
        full_path = f"{path}/{key}"
        if isinstance(obj, uproot.behaviors.TTree.TTree):
            branches = [{"label": branch, "value": f"{full_path}/{branch}", "selectable": True} for branch in obj.keys()]
            nodes.append({"label": key, "value": full_path, "children": branches, "selectable": False})
        elif isinstance(obj, uproot.reading.ReadOnlyDirectory):
            children = build_tree_nodes(obj, path=full_path)
            nodes.append({"label": key, "value": full_path, "children": children, "selectable": False})
    return nodes

# Function to plot histogram of a selected branch
def plot_branch_histogram(tree, branch):
    """
    Plots the histogram of a selected branch from the ROOT TTree.
    """
    data = tree[branch].array(library="np")
    
    # Ensure data is numerical
    if data.dtype == np.bool_:
        data = data.astype(np.int_)

    fig, ax = plt.subplots()
    ax.hist(data, bins=30, alpha=0.7, color="skyblue")
    ax.set_title(f"Histogram of {branch}")
    ax.set_xlabel("Value")
    ax.set_ylabel("Frequency")
    st.pyplot(fig)

if file_path:
    # Load the ROOT file using uproot
    file = uproot.open(file_path)
    
    # Build and display the tree structure
    nodes = build_tree_nodes(file)
    selected_nodes = tree_select(nodes, key="tree_select")

    if selected_nodes:
        for node in selected_nodes['checked']:
            parts = node.split("/")
            if len(parts) > 2:
                tree = file[parts[1]]
                plot_branch_histogram(tree, parts[2])
else:
    st.sidebar.write("Upload a ROOT file to start exploring.")
