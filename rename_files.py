import os
import sys

def rename_pdfs():
    current_dir = os.getcwd()
    print(current_dir)
    id = None
    try: 
        id = int(sys.argv[1])
        print(id)
    except ValueError: 
        print("invalid id arg")
        sys.exit(1)
    
    for filename in os.listdir(current_dir):
        if filename.endswith('.pdf'):
            name_parts = filename.replace('.pdf', '').split('_')
            date_part = name_parts[0]
            # name_part = name_parts[1]

            new_filename = f"Prefix_{id}_{date_part}.pdf"
            old_filepath = os.path.join(current_dir, filename)
            new_filepath = os.path.join(current_dir, new_filename)
            
            os.rename(old_filepath, new_filepath)
            print(f"renamed '{filename}' to '{new_filename}'")

if __name__ == "__main__":
    rename_pdfs()
