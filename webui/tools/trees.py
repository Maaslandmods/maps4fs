import os
import streamlit as st
import json
import config
from config import is_on_community_server, is_public
from tools.tool import Tool
from templates import Messages

class CreateTreeSchema(Tool):
    title = "Tree schema"
    description = "Visually create your custom tree schema."
    icon = "🌳"

    def content(self):
        if is_on_community_server() or is_public():
            st.warning(Messages.TOOL_LOCAL)
            return

        st.write(Messages.TEXTURE_SCHEMA_INFO)

        @st.cache_data
        def load_tree_data():
            with open(config.FS25_TREE_SCHEMA_PATH, "r", encoding="utf-8") as f:
                tree_schema = json.load(f)
            tree_images_path = "data/tree_images"
            tree_options = [
                {"name": tree["name"], "image": os.path.join(tree_images_path, f"{tree['name']}.png")}
                for tree in tree_schema
            ]
            return tree_schema, tree_options

        tree_schema, tree_options = load_tree_data()

        STATE_PREFIX = "tree_schema_creator_"

        if f"{STATE_PREFIX}selected_trees" not in st.session_state:
            # Initialize with all tree names to have them selected by default
            st.session_state[f"{STATE_PREFIX}selected_trees"] = [tree["name"] for tree in tree_options]

        if st.button("Save Tree Schema"):
            filtered_tree_schema = [
                tree for tree in tree_schema if tree["name"] in st.session_state[f"{STATE_PREFIX}selected_trees"]
            ]
            output_path = config.FS25_TREE_SCHEMA_PATH
            with open(output_path, "w") as f:
                json.dump(filtered_tree_schema, f, indent=4)
            st.success("Tree custom schema successfully saved, it can be found in the Expert Settings.")

        st.write("Select trees for the custom schema:")
        columns = st.columns(6)

        for idx, tree in enumerate(tree_options):
            col = columns[idx % 6]
            with col:
                st.image(tree["image"], caption=tree["name"], use_container_width=True)
                toggle_key = f"{STATE_PREFIX}tree_toggle_{tree['name']}"

                if toggle_key not in st.session_state:
                    # Set the toggle state to True by default
                    st.session_state[toggle_key] = True

                if st.button(
                    label="On" if st.session_state[toggle_key] else "Off",
                    key=f"{toggle_key}_button"
                ):
                    st.session_state[toggle_key] = not st.session_state[toggle_key]

                if st.session_state[toggle_key] and tree["name"] not in st.session_state[f"{STATE_PREFIX}selected_trees"]:
                    st.session_state[f"{STATE_PREFIX}selected_trees"].append(tree["name"])
                elif not st.session_state[toggle_key] and tree["name"] in st.session_state[f"{STATE_PREFIX}selected_trees"]:
                    st.session_state[f"{STATE_PREFIX}selected_trees"].remove(tree["name"])