import re

def find_and_remove_items(file_path, descriptions=None, names=None, remove_reports=False):
    """
    Find and remove items and reports from audit files.

    Args:
        file_path (str): Path to the audit file
        descriptions (list): List of descriptions to match
        names (list): List of names to match
        remove_reports (bool): Whether to remove report sections

    Returns:
        tuple: (items_removed, reports_removed)
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    with open(file_path + '.backup', 'w', encoding='utf-8') as backup:
        backup.write(content)

    items_to_remove = []
    reports_removed = 0

    # Remove report sections if requested
    if remove_reports:
        content, reports_removed = remove_report_sections(content)

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

    for start, end in sorted(items_to_remove, reverse=True):
        content = content[:start] + content[end:]

    content = re.sub(r'\n{3,}', '\n\n', content)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

    return len(items_to_remove), reports_removed

def remove_report_sections(content):
    """
    Remove all report sections from the content.
    """
    report_pattern = r'<report\s+type\s*:\"[^\"]*\">.*?</report>'
    reports = list(re.finditer(report_pattern, content, re.DOTALL))

    for match in reversed(reports):
        start = match.start()
        while start > 0 and content[start-1].isspace():
            start -= 1
        content = content[:start] + content[match.end():]

    return content, len(reports)

def print_all_items(file_path):
    """Print all items in the file for verification purposes."""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    item_pattern = r'<(?:custom_)?item>.*?</(?:custom_)?item>'
    report_pattern = r'<report\s+type\s*:\"[^\"]*\">.*?</report>'

    items = re.finditer(item_pattern, content, re.DOTALL)
    reports = re.finditer(report_pattern, content, re.DOTALL)

    print("\nCurrent items in file:")
    for i, item in enumerate(items, 1):
        desc_match = re.search(r'description\s*:\s*"([^"]*)"', item.group())
        if desc_match:
            print(f"{i}. {desc_match.group(1)}")

    print("\nCurrent reports in file:")
    for i, report in enumerate(reports, 1):
        report_content = report.group()
        type_match = re.search(r'type\s*:\"([^\"]*)\"', report_content)
        desc_match = re.search(r'description\s*:\s*"([^"]*)"', report_content)
        print(f"\nReport {i}:")
        if type_match:
            print(f"Type: {type_match.group(1)}")
        if desc_match:
            print(f"Description: {desc_match.group(1)}")
        print("-" * 50)

if __name__ == "__main__":
    audit_file = "aix_7.3.audit"

    print("Items before removal:")
    print_all_items(audit_file)

    descriptions_to_remove = [
        "2.3 Allowlist Authorized Software and Report Validations"
    ]

    names_to_remove = [
        "passwd_duplicate_username",
    ]

    try:
        items_removed, reports_removed = find_and_remove_items(
            audit_file,
            descriptions=descriptions_to_remove,
            names=names_to_remove,
            remove_reports=True
        )

        print(f"\nSuccessfully removed {items_removed} items and {reports_removed} reports")
        print(f"Backup created at: {audit_file}.backup")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
