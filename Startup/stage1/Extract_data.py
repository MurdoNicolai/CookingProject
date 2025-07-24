#!/usr/bin/env python
def extract_data(filename):
    """Reads a text file and returns its content as a list of lines."""
    with open("example_recipes/" + filename, 'r', encoding='utf-8') as file:
        return file.readlines()

# Example usage
data = extract_data("recipe 5.txt")
print(data)


