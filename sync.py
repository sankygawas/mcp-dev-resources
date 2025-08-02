#!/usr/bin/env python3
"""
Simple script to update README.md content from Notion CSV export
Only updates the "Resources by Category" section to preserve manual edits
Usage: python sync.py
"""

import csv
import os
import re
from collections import defaultdict

def format_stars(stars_str):
    """Format GitHub stars with k suffix"""
    if not stars_str or stars_str == '':
        return '-'
    
    try:
        # Handle comma-separated numbers like "2,600"
        stars_str = stars_str.replace(',', '')
        stars = float(stars_str)
        
        if stars >= 1000:
            return f"⭐ {stars/1000:.1f}k".rstrip('0').rstrip('.')
        else:
            return f"⭐ {int(stars)}"
    except (ValueError, TypeError):
        return '-'

def format_description(desc):
    """Truncate description if too long"""
    if len(desc) > 120:
        return desc[:117] + "..."
    return desc

def generate_categories_content(resources_by_category):
    """Generate the Resources by Category section"""
    content = "## 📚 Resources by Category\n\n"
    
    # Add each category section
    for category, resources in sorted(resources_by_category.items()):
        content += f"### {category}\n\n"
        content += "| Name | Connection Type | Stars | Description |\n"
        content += "|------|----------------|-------|-------------|\n"
        
        for resource in sorted(resources, key=lambda x: x['MCP Name']):
            name = resource['MCP Name']
            connection = resource['Connection Type']
            github_link = resource['GitHub Link']
            stars = format_stars(resource['GitHub Stars'])
            description = format_description(resource['Social Sentiment TLDR'])
            
            # Create clickable name if GitHub link exists
            if github_link and github_link.startswith('http'):
                name_link = f"[{name}]({github_link})"
            else:
                name_link = name
            
            content += f"| {name_link} | {connection} | {stars} | {description} |\n"
        
        content += "\n"
    
    return content

def main():
    # Find the CSV file
    csv_file = None
    for file in os.listdir('notion-dataset'):
        if file.endswith('.csv') and not file.endswith('_all.csv'):
            csv_file = f'notion-dataset/{file}'
            break
    
    if not csv_file:
        print("❌ No CSV file found in notion-dataset folder")
        return
    
    print(f"📁 Reading {csv_file}")
    
    # Read CSV and organize by category
    resources_by_category = defaultdict(list)
    total_count = 0
    
    with open(csv_file, 'r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['MCP Name']:  # Skip empty rows
                resources_by_category[row['Category']].append(row)
                total_count += 1
    
    # Read existing README.md
    try:
        with open('README.md', 'r', encoding='utf-8') as file:
            readme_content = file.read()
    except FileNotFoundError:
        print("❌ README.md not found")
        return
    
    # Generate new categories content
    new_categories_content = generate_categories_content(resources_by_category)
    
    # Find and replace the Resources by Category section
    # Pattern matches from "## 📚 Resources by Category" to the end of file
    pattern = r'(## 📚 Resources by Category.*?)$'
    
    if re.search(pattern, readme_content, re.DOTALL):
        # Replace existing section
        updated_content = re.sub(pattern, new_categories_content.rstrip(), readme_content, flags=re.DOTALL)
    else:
        # Append if section doesn't exist
        updated_content = readme_content + "\n\n" + new_categories_content
    
    # Write updated README.md
    with open('README.md', 'w', encoding='utf-8') as file:
        file.write(updated_content)
    
    print(f"✅ Updated README.md with {total_count} resources across {len(resources_by_category)} categories")
    print("📝 Only the 'Resources by Category' section was updated - other content preserved")

if __name__ == "__main__":
    main()