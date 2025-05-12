import subprocess
import os
import tempfile
import json
import re

def blockchain_call(program_name, function_name, inputs, project_path=None, 
                   is_deployed=False, network=None, endpoint=None):
    """
    Call an Aleo program function using Leo CLI
    
    Args:
        program_name: Name of the Aleo program
        function_name: Function to call
        inputs: List of input parameters
        project_path: Path to Leo project
        is_deployed: Whether to run on deployed program
        network: Network to use (e.g., "testnet")
        endpoint: API endpoint for the network
    """
    # Always quote arguments for Leo CLI
    input_args = [f'"{str(arg)}"' for arg in inputs]
    formatted_inputs = " ".join(input_args)
    
    # Create temp file for output
    with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as tmp:
        output_file = tmp.name
    
    # Get project path
    if project_path is None:
        project_path = os.getcwd()
    
    # Build command
    if is_deployed or True:  # Always use leo run
        network_flag = f"--network {network}" if network else ""
        endpoint_flag = f"--endpoint \"{endpoint}\"" if endpoint else ""
        base_cmd = f"cd {project_path} && leo run {function_name} {formatted_inputs} {network_flag} {endpoint_flag}"
    else:
        base_cmd = f"cd {project_path} && leo execute {program_name} {function_name} {formatted_inputs}"
    
    # Use WSL on Windows
    cmd = f"wsl -- bash -c '{base_cmd}'" if os.name == 'nt' else base_cmd
    
    try:
        print(f"Executing: {cmd}")
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        output = result.stdout

        # Try to parse JSON from output, or just return the output
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            return {"success": True, "raw_output": output.strip()}

    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
        print(f"Error output: {e.stderr if hasattr(e, 'stderr') else ''}")
        return {"success": False, "error": str(e)}
    finally:
        try:
            os.unlink(output_file)
        except:
            pass

def extract_leo_output(raw_output):
    """
    Extracts the output record (the curly-brace block) from Leo CLI output.
    Returns the record as a string, or None if not found.
    """
    # Find the "Output" section and the first curly-brace block after it
    match = re.search(r"Output\s*\n\s*•\s*({.*?})", raw_output, re.DOTALL)
    if match:
        record_str = match.group(1)
        return record_str.strip()
    return None