import sys

# Read the file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the return statement
old_code = """            return jsonify({
                'response': response,
                'status': 'success'
            })"""

new_code = """            # Save assistant response to database
            if chat_db and chat_id:
                chat_db.add_message(chat_id, 'assistant', response)
            
            return jsonify({
                'response': response,
                'chat_id': chat_id,
                'status': 'success'
            })"""

# Replace
if old_code in content:
    updated_content = content.replace(old_code, new_code, 1)
    
    # Write back
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("✓ Successfully updated app.py with chat history save logic!")
else:
    print("✗ Could not find the code to replace. It may have already been updated.")
    sys.exit(1)
