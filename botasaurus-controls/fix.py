def update_section_controls(file_path):
    start_phrase = "declare class Controls {"
    end_phrase = "declare function createControls"
    new_start_phrase = "declare class SectionControls {"
    
    with open(file_path, "r") as file:
        lines = file.readlines()
    
    # Find start and end indices
    start_index = end_index = None
    for i, line in enumerate(lines):
        if start_phrase in line:
            start_index = i
        elif end_phrase in line and start_index is not None:
            end_index = i
            break
    
    # If start and end found, process the block
    if start_index is not None and end_index is not None:
        # Copy and modify the block
        section_controls_block = [new_start_phrase + "\n"] + lines[start_index + 1:end_index]
        # Remove the line containing 'section(label: string,'
        section_controls_block = [line for line in section_controls_block if 'section(label: string,' not in line]
        # Replace the 'type SectionControls' line with the new block
        # lines = lines[:start_index] + section_controls_block + lines[end_index + 1:]
    # type SectionControls = Omit<Controls, "section">;
    # Write the modified content back to the file
    
    with open(file_path, "r") as file:
        x = file.read()
        x =  x.replace('type SectionControls = Omit<Controls, "section">;', "".join( section_controls_block).strip())

    with open(file_path, "w") as file:
        file.write(x)


# Replace 'dist/index.d.ts' with the actual path to your file
update_section_controls('dist/index.d.ts')
