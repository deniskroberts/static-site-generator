import re

from textnode import (
    TextNode,
    text_type_text,
    text_type_bold,
    text_type_italic,
    text_type_code,
    text_type_link,
    text_type_image,
)


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != text_type_text:
            new_nodes.append(old_node)
            continue
        split_nodes = []
        sections = old_node.text.split(delimiter)
        if len(sections) % 2 == 0:
            raise ValueError("Invalid markdown, formatted section not closed")
        for i in range(len(sections)):
            if sections[i] == "":
                continue
            if i % 2 == 0:
                split_nodes.append(TextNode(sections[i], text_type_text))
            else:
                split_nodes.append(TextNode(sections[i], text_type))
        new_nodes.extend(split_nodes)
    return new_nodes

def extract_markdown_images(text):
    pattern = r"!\[(.*?)]\((.*?)\)"
    matches = re.findall(pattern, text)
    return matches

def extract_markdown_links(text):
    pattern = r"(?<!!)\[(.*?)\]\((.*?)\)"
    matches = re.findall(pattern, text)
    return matches

def split_nodes_image(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != text_type_text:
            new_nodes.append(old_node)
            continue

        images = extract_markdown_images(old_node.text)
        if not images:
            new_nodes.append(old_node)
            continue

        current_index = 0
        for alt_text, url in images:
            image_markdown = f"![{alt_text}]({url})"
            start_index = old_node.text.index(image_markdown, current_index)
            end_index = start_index + len(image_markdown)

            if start_index > current_index:
                text_before = old_node.text[current_index:start_index]
                if text_before.strip():
                    new_nodes.append(TextNode(text_before, text_type_text))

            new_nodes.append(TextNode(alt_text, text_type_image, url))
            current_index = end_index

        if current_index < len(old_node.text):
            remaining_text = old_node.text[current_index:]
            if remaining_text.strip():
                new_nodes.append(TextNode(remaining_text, text_type_text))

    return new_nodes

def split_nodes_link(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != text_type_text:
            new_nodes.append(old_node)
            continue
        
        links = extract_markdown_links(old_node.text)
        if not links:
            new_nodes.append(old_node)
            continue
        
        current_index = 0
        for link_text, url in links:
            link_markdown = f"[{link_text}]({url})"
            start_index = old_node.text.find(link_markdown, current_index)
            
            if start_index > current_index:
                new_nodes.append(TextNode(old_node.text[current_index:start_index], text_type_text))
            
            new_nodes.append(TextNode(link_text, text_type_link, url))
            current_index = start_index + len(link_markdown)
        
        if current_index < len(old_node.text):
            new_nodes.append(TextNode(old_node.text[current_index:], text_type_text))
    
    return new_nodes
