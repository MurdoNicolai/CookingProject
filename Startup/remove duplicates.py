
unique_lines = []
with open("file_sections.txt", 'r') as infile:
    lines = infile.readlines()
seen = set()
for line in lines:
    if line not in seen:
        unique_lines.append(line)
        seen.add(line)
with open("file_sections.txt", 'w') as outfile:
    for line in unique_lines:
        outfile.write(line)