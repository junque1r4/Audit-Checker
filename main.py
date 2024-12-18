import re

def find_and_remove_items(file_path, descriptions=None, remove_reports=False):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        with open(file_path + '.backup', 'w', encoding='utf-8') as backup:
            backup.write(content)

        items_removed = 0
        reports_removed = 0

        # Remove items
        item_pattern = r'(?:\s*)<(?:custom_)?item>.*?</(?:custom_)?item>'
        for desc in descriptions:
            desc_pattern = f'description\\s*:\\s*"{re.escape(desc)}"'
            matches = list(re.finditer(item_pattern, content, re.DOTALL))

            for match in reversed(matches):
                item_content = match.group()
                if re.search(desc_pattern, item_content, re.IGNORECASE):
                    start = match.start()
                    while start > 0 and content[start-1].isspace():
                        start -= 1
                    content = content[:start] + content[match.end():]
                    items_removed += 1

        # Remove reports if requested
        if remove_reports and descriptions:
            report_pattern = r'<report\s+type\s*:\"[^\"]*\">.*?</report>'
            matches = list(re.finditer(report_pattern, content, re.DOTALL))

            for match in reversed(matches):
                report_content = match.group()
                for desc in descriptions:
                    desc_pattern = f'description\\s*:\\s*"{re.escape(desc)}"'
                    if re.search(desc_pattern, report_content, re.IGNORECASE):
                        start = match.start()
                        while start > 0 and content[start-1].isspace():
                            start -= 1
                        content = content[:start] + content[match.end():]
                        reports_removed += 1
                        break

        content = re.sub(r'\n{3,}', '\n\n', content)

        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)

        print(f"\nRemoved {items_removed} items and {reports_removed} reports")
        return items_removed, reports_removed

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return 0, 0

def print_all_items(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        item_pattern = r'<(?:custom_)?item>.*?</(?:custom_)?item>'
        report_pattern = r'<report\s+type\s*:\"[^\"]*\">.*?</report>'

        print("\nCurrent items in file:")
        items = list(re.finditer(item_pattern, content, re.DOTALL))
        for i, item in enumerate(items, 1):
            desc_match = re.search(r'description\s*:\s*"([^"]*)"', item.group())
            if desc_match:
                print(f"{i}. {desc_match.group(1)}")
        print(f"Total items: {len(items)}")

        print("\nCurrent reports in file:")
        reports = list(re.finditer(report_pattern, content, re.DOTALL))
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
        print(f"Total reports: {len(reports)}")

    except Exception as e:
        print(f"An error occurred while printing items: {str(e)}")

if __name__ == "__main__":
    audit_file = "aix_7.3.audit"

    print("Items before removal:")
    print_all_items(audit_file)

    descriptions_to_remove = [
        "2.1.1 Ensure Trusted Execution Path is enabled",
        "4.2.6 Ensure that host based authentication files are not present",
        "4.3.2.9 Ensure mrouted is not in use",
    ]

    items_removed, reports_removed = find_and_remove_items(
        audit_file,
        descriptions=descriptions_to_remove,
        remove_reports=True
    )

    if items_removed > 0 or reports_removed > 0:
        print(f"Backup created at: {audit_file}.backup")
        print("\nRemaining items after removal:")
        print_all_items(audit_file)
