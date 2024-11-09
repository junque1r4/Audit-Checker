import re

def find_and_remove_items(file_path, descriptions=None, names=None):
    """
    A simplified approach to find and remove items from audit files.
    Uses string indexes to precisely locate and remove items.

    Args:
        file_path (str): Path to the audit file
        descriptions (list): List of descriptions to match
        names (list): List of names to match

    Returns:
        int: Number of items removed
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    with open(file_path + '.backup', 'w', encoding='utf-8') as backup:
        backup.write(content)

    items_to_remove = []

    item_starts = [(match.start(), match.group())
                   for match in re.finditer(r'(?:\s*)<(?:custom_)?item>\s*\n', content)]

    item_ends = [(match.end(), match.group())
                 for match in re.finditer(r'\s*</(?:custom_)?item>', content)]

    if len(item_starts) != len(item_ends):
        raise ValueError(f"Mismatched item tags: {len(item_starts)} openings vs {len(item_ends)} closings")

    for (start_pos, start_tag), (end_pos, end_tag) in zip(item_starts, item_ends):
        item_content = content[start_pos:end_pos]

        should_remove = False

        if descriptions:
            for desc in descriptions:
                desc_pattern = f'description\\s*:\\s*"{re.escape(desc)}"'
                if re.search(desc_pattern, item_content):
                    should_remove = True
                    break

        if names and not should_remove:
            for name in names:
                name_pattern = f'name\\s*:\\s*"{re.escape(name)}"'
                if re.search(name_pattern, item_content):
                    should_remove = True
                    break

        if should_remove:
            real_start = start_pos
            while real_start > 0 and content[real_start-1].isspace():
                real_start -= 1

            items_to_remove.append((real_start, end_pos))

    new_content = content
    for start, end in sorted(items_to_remove, reverse=True):
        new_content = new_content[:start] + new_content[end:]

    new_content = re.sub(r'\n{3,}', '\n\n', new_content)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(new_content)

    return len(items_to_remove)

def print_all_items(file_path):
    """
    Print all items in the file for verification purposes.

    Args:
        file_path (str): Path to the audit file
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    item_pattern = r'(?:\s*)<(?:custom_)?item>.*?</(?:custom_)?item>'
    items = re.finditer(item_pattern, content, re.DOTALL)

    print("\nCurrent items in file:")
    for i, item in enumerate(items, 1):
        item_content = item.group()
        desc_match = re.search(r'description\s*:\s*"([^"]*)"', item_content)
        name_match = re.search(r'name\s*:\s*"([^"]*)"', item_content)

        print(f"\nItem {i}:")
        if desc_match:
            print(f"Description: {desc_match.group(1)}")
        if name_match:
            print(f"Name: {name_match.group(1)}")
        print("-" * 50)

if __name__ == "__main__":
    audit_file = "teste_audit_rhel8.audit"

    print("Items before removal:")
    print_all_items(audit_file)

    descriptions_to_remove = [
        "6.2.6 Ensure no duplicate user names exist",
    ]

    names_to_remove = [
        "passwd_duplicate_username",
    ]

    try:
        removed_count = find_and_remove_items(
            audit_file,
            descriptions=descriptions_to_remove,
            names=names_to_remove
        )

        print(f"\nSuccessfully removed {removed_count} items")
        print(f"Backup created at: {audit_file}.backup")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
