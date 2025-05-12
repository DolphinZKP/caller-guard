# caller-guard/utils/blockchain.py
import subprocess
import json
import os
import tempfile
import time

def blockchain_call(program_name, function_name, inputs, project_path=None):
    """Call an Aleo program function using CLI"""
    # Format inputs
    input_args = []
    for input_val in inputs:
        if isinstance(input_val, str) and not input_val.endswith("field"):
            input_args.append(f'"{input_val}"')
        else:
            input_args.append(str(input_val))
    
    formatted_inputs = " ".join(input_args)
    
    # Create temp file for output
    with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as tmp:
        output_file = tmp.name
    
    # Get project path
    if project_path is None:
        project_path = os.getcwd()
    
    # Build command
    base_cmd = f"cd {project_path} && leo execute {program_name} {function_name} {formatted_inputs} --output {output_file}"
    cmd = f"wsl -- bash -c '{base_cmd}'" if os.name == 'nt' else base_cmd
    
    # Execute
    try:
        subprocess.run(cmd, shell=True, check=True)
        
        # Read output
        if os.name == 'nt':
            wsl_path = output_file.replace('\\', '/')
            if wsl_path[1] == ':':
                drive = wsl_path[0].lower()
                wsl_path = f"/mnt/{drive}{wsl_path[2:]}"
            file_content = subprocess.check_output(f'wsl -- cat "{wsl_path}"', shell=True, text=True)
        else:
            with open(output_file, 'r') as f:
                file_content = f.read()
        
        # Parse result
        return json.loads(file_content) if file_content.strip() else {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        try:
            os.unlink(output_file)
        except:
            pass