def merge_and_sort_items(folders, files):
    merged_structure = []

    # Append folders to merged structure
    for folder in folders:
        merged_structure.append({
            'id': folder['id'],
            'title': folder['title'],
            'type': 'folder',
            'parent_id': folder.get('parent'),  # Use parent ID if available
            'created': folder['created'],
            'order': folder['order']
        })

    # Append contents to merged structure
    for file in files:
        merged_structure.append({
            'id': file['id'],
            'title': file['title'],  # Assuming 'document' is the title
            'type': 'file',
            'url': file['url'],
            'is_locked': file['is_locked'],
            'folder_id': file['folder'],  # Link to folder ID
            'created': file['created'],
            'order': file['order']
        })

    # Sort by 'created' date
    return sorted(merged_structure, key=lambda x: x['order'])
